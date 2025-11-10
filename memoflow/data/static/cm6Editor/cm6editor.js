import "https://cdn.jsdelivr.net/gh/qyzhizi/chun-mde-dist@v0.1.0/dist/chunmde.bundle.min.js";


const { 
  createChunEditor, 
  createImageUploadPlugin, 
  createMarkdownPreviewPlugin, 
  githubPreviewConfig, 
  darkPreviewConfig 
} = Chun;

/**
 * 创建并返回一个 ChunMDE 编辑器实例
 * @param {string} containerId - 容器 ID
 * @param {string} initialContent - 初始 Markdown 内容
 * @returns editor 实例
 */
export function createEditor(containerId = "editor-container", initialContent = "# Markdown Editor") {
  // 图片上传插件
  const imageUploadPlugin = createImageUploadPlugin({
    imageUploadUrl: "", 
    imageFormats: ["image/jpg", "image/jpeg", "image/gif", "image/png", "image/bmp", "image/webp"],
  });

  // Markdown 预览插件
  const MarkdownPreviewPlugin = createMarkdownPreviewPlugin(githubPreviewConfig);

  // 初始化编辑器
  const editor = createChunEditor({
    doc: initialContent,
    lineWrapping: true,
    indentWithTab: true,
    toolbar: true,
    theme: "dark",
  })
  .use(imageUploadPlugin)
  .use(MarkdownPreviewPlugin)
  .mount(containerId);

  return editor;
}
