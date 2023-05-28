# -*- coding: UTF-8 -*-
import os
import signal
import time
import logging
import errno
import sys
import eventlet.wsgi
import eventlet
from eventlet.green import socket
from eventlet.green import ssl

LOG = logging.getLogger(__name__)

URL_LENGTH_LIMIT = 50000


def get_bind_addr(conf, default_port=None):
    """Return the host and port to bind to."""
    return (conf.get("bind_host") or '0.0.0.0',
            int(conf.get("port")) or default_port)


def get_socket(conf, default_port):
    """Bind socket to bind ip:port in conf.

    Note: Mostly comes from Swift with a few small changes...

    :param conf: a cfg.ConfigOpts object
    :param default_port: port to bind to if none is specified in conf

    :returns : a socket object as returned from socket.listen or
               ssl.wrap_socket if conf specifies cert_file
    """
    bind_addr = get_bind_addr(conf, default_port)
    address_family = [addr[0] for addr in socket.getaddrinfo(bind_addr[0],
                                                             bind_addr[1], socket.AF_UNSPEC, socket.SOCK_STREAM)
                      if addr[0] in (socket.AF_INET, socket.AF_INET6)][0]

    cert_file = conf.get("cert_file")
    key_file = conf.get("key_file")
    use_ssl = cert_file or key_file
    if use_ssl and (not cert_file or not key_file):
        raise RuntimeError(_("When running server in SSL mode, you must "
                             "specify both a cert_file and key_file "
                             "option value in your configuration file"))

    sock = None
    retry_until = time.time() + 30
    while not sock and time.time() < retry_until:
        try:
            sock = eventlet.listen(bind_addr,
                                   family=address_family)
        except socket.error as err:
            if err.args[0] != errno.EADDRINUSE:
                raise
            eventlet.sleep(0.1)
    if not sock:
        raise RuntimeError(_("Could not bind to %(bind_addr)s "
                             "after trying for 30 seconds")
                           % {'bind_addr': bind_addr})

    return sock


class Server(object):
    """Server class to manage multiple WSGI sockets and applications."""

    def __init__(self, conf, threads=1000):
        os.umask(0o27)  # ensure files are created with the correct privileges
        self._logger = logging.getLogger("eventlet.wsgi.server")
        self.threads = threads
        self.children = set()
        self.stale_children = set()
        self.running = True
        self.pgid = os.getpid()
        self.conf = conf
        #print("self.conf:", self.conf)
        try:
            os.setpgid(self.pgid, self.pgid)
        except OSError:
            self.pgid = 0

    def kill_children(self, *args):
        """Kills the entire process group."""
        LOG.error('SIGTERM received')
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.running = False
        os.killpg(0, signal.SIGTERM)

    def hup(self, *args):
        """Reloads configuration files with zero down time."""
        LOG.error('SIGHUP received')
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        raise Exception("hup exception")

    def start(self, application):
        """Run a WSGI server with the given application.

        :param application: The application to run in the WSGI server
        :param default_port: Port to bind to if none is specified in conf
        """

        eventlet.wsgi.MAX_HEADER_LINE = int(self.conf.get("max_header_line"))
        self.application = application
        self.default_port = int(self.conf.get("port"))
        self.configure_socket()
        self.start_wsgi()

    def start_wsgi(self):
        workers = int(self.conf.get("workers"))
        if workers == 1:
            # Useful for profiling, test, debug etc.
            self.pool = eventlet.GreenPool(size=self.threads)
            self.pool.spawn_n(self._single_run, self.application, self.sock)
            return
        # childs equal specified value of workers
        else:
            childs_num = workers

        LOG.info("Starting %d workers", workers)
        signal.signal(signal.SIGTERM, self.kill_children)
        signal.signal(signal.SIGINT, self.kill_children)
        signal.signal(signal.SIGHUP, self.hup)
        while len(self.children) < childs_num:
            self.run_child()

    def wait_on_children(self):
        while self.running:
            try:
                # 进程常驻
                pid, status = os.wait()
                # 进程因exit退出或者 signal退出
                if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                    self._remove_children(pid)
                    self._verify_and_respawn_children(pid, status)
            except OSError as err:
                if err.errno not in (errno.EINTR, errno.ECHILD):
                    raise
            except KeyboardInterrupt:
                LOG.info('Caught keyboard interrupt. Exiting.')
                os.killpg(0, signal.SIGTERM)
                break
            except Exception:
                continue
        eventlet.greenio.shutdown_safe(self.sock)
        self.sock.close()
        LOG.debug('Exited')

    def _verify_and_respawn_children(self, pid, status):
        if len(self.stale_children) == 0:
            LOG.debug('No stale children')
        if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
            LOG.error('Not respawning child %d, cannot '
                      'recover from termination', pid)
            if not self.children and not self.stale_children:
                LOG.info(
                    'All workers have terminated. Exiting')
                self.running = False
        else:
            if len(self.children) < self.conf.workers:
                self.run_child()

    def configure_socket(self, old_conf=None, has_changed=None):
        """Ensure a socket exists and is appropriately configured.

        This function is called on start up, and can also be
        called in the event of a configuration reload.

        When called for the first time a new socket is created.
        If reloading and either bind_host or bind port have been
        changed the existing socket must be closed and a new
        socket opened (laws of physics).

        In all other cases (bind_host/bind_port have not changed)
        the existing socket is reused.

        :param old_conf: Cached old configuration settings (if any)
        :param has changed: callable to determine if a parameter has changed
        """
        # Do we need a fresh socket?
        new_sock = (old_conf is None or (
                has_changed('bind_host') or
                has_changed('bind_port')))
        # Will we be using https?
        use_ssl = not (not self.conf.get("cert_file") or not self.conf.get("key_file"))
        # Were we using https before?
        old_use_ssl = (old_conf is not None and not (
                not old_conf.get('key_file') or
                not old_conf.get('cert_file')))
        # Do we now need to perform an SSL wrap on the socket?
        wrap_sock = use_ssl is True and (old_use_ssl is False or new_sock)
        # Do we now need to perform an SSL unwrap on the socket?
        unwrap_sock = use_ssl is False and old_use_ssl is True

        if new_sock:
            self._sock = None
            if old_conf is not None:
                self.sock.close()
            _sock = get_socket(self.conf, self.default_port)
            _sock.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)
            # sockets can hang around forever without keepalive
            _sock.setsockopt(socket.SOL_SOCKET,
                             socket.SO_KEEPALIVE, 1)
            self._sock = _sock

        if wrap_sock:
            self.sock = ssl.wrap_socket(self._sock,
                                        certfile=self.conf.cert_file,
                                        keyfile=self.conf.key_file)

        if unwrap_sock:
            self.sock = self._sock

        if new_sock and not use_ssl:
            self.sock = self._sock

        # Pick up newly deployed certs
        if old_conf is not None and use_ssl is True and old_use_ssl is True:
            if has_changed('cert_file'):
                self.sock.certfile = self.conf.get("cert_file")
            if has_changed('key_file'):
                self.sock.keyfile = self.conf.get("key_file")

        if new_sock or (old_conf is not None and has_changed('tcp_keepidle')):
            # This option isn't available in the OS X version of eventlet
            if hasattr(socket, 'TCP_KEEPIDLE'):
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, True)

        if old_conf is not None and has_changed('backlog'):
            self.sock.listen(self.conf.get("backlog"))

    def _remove_children(self, pid):
        if pid in self.children:
            self.children.remove(pid)
            LOG.info('Removed dead child %s', pid)
        elif pid in self.stale_children:
            self.stale_children.remove(pid)
            LOG.info('Removed stale child %s', pid)
        else:
            LOG.warning('Unrecognised child %s', pid)

    def wait(self):
        """Wait until all servers have completed running."""
        try:
            if self.children:
                self.wait_on_children()
            else:
                self.pool.waitall()
        except KeyboardInterrupt:
            pass

    def run_child(self):
        def child_hup(*args):
            """Shuts down child processes, existing requests are handled."""
            signal.signal(signal.SIGHUP, signal.SIG_IGN)
            eventlet.wsgi.is_accepting = False
            self.sock.close()

        pid = os.fork()
        if pid == 0:
            signal.signal(signal.SIGHUP, child_hup)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            # ignore the interrupt signal to avoid a race whereby
            # a child worker receives the signal before the parent
            # and is respawned unnecessarily as a result
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            # The child has no need to stash the unwrapped
            # socket, and the reference prevents a clean
            # exit on sighup
            self._sock = None
            self.run_server()
            LOG.info('Child %d exiting normally', os.getpid())
            # self.pool.waitall() is now called in wsgi's server so
            # it's safe to exit here
            sys.exit(0)
        else:
            LOG.info('Started child %s', pid)
            self.children.add(pid)

    def run_server(self):
        """Run a WSGI server."""
        eventlet.wsgi.HttpProtocol.default_request_version = "HTTP/1.0"
        eventlet.hubs.use_hub('poll')
        eventlet.patcher.monkey_patch(all=False, socket=True)
        self.pool = eventlet.GreenPool(size=self.threads)
        socket_timeout = None
        try:
            eventlet.wsgi.server(
                self.sock,
                self.application,
                custom_pool=self.pool,
                url_length_limit=URL_LENGTH_LIMIT,
                log=self._logger,
                debug=True,
                keepalive=True,
                socket_timeout=socket_timeout)
        except socket.error as err:
            if err[0] != errno.EINVAL:
                raise
        self.pool.waitall()

    def _single_run(self, application, sock):
        """Start a WSGI server in a new green thread."""
        LOG.info("Starting single process server")
        eventlet.wsgi.server(sock, application,
                             custom_pool=self.pool,
                             url_length_limit=URL_LENGTH_LIMIT,
                             log=self._logger,
                             debug=True)
