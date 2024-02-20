import os
def paths_to_table_names(file_list):
    """
    :param file_list: 
        e.g.: 'pages/github_cards_2.md, pages/github_cards_test.md'
    :return: 
        e.g. : (['pages/github_cards_2.md', 'pages/github_cards_test.md'], 
               ['github_cards_2', 'github_cards_test'])
    """
    if file_list is not None:
        sync_file_paths = file_list.split(",")
        sync_table_names = []
        # remove empty string, and strip space
        for idx, file_path in enumerate(sync_file_paths):
            if file_path.strip() == "":
                sync_file_paths.remove(file_path)
            else:
                file_path = file_path.strip()
                sync_file_paths[idx] = file_path
                file_name = os.path.basename(file_path)
                sync_table_names.append(file_name.split(".")[0])
    return sync_file_paths, sync_table_names

if __name__ == "__main__":
    x, y =paths_to_table_names("pages/github_cards_2.md, ")
    print(x,y)
    x, y = paths_to_table_names(" pages/github_cards_2.md , pages/github_cards_test.md ")
    print(x, y)