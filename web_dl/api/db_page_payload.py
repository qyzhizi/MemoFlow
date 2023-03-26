def get_payload(database_id, title_content, txt_content, tags, txt_content_link=''):
    payload = {
        "parent": {
            "database_id": database_id
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title_content
                        }
                    }
                ]
            },
            # 完整的格式：
            # "Tags":{"id":"lfnl","type":"multi_select", "multi_select":[{"id":"aae98d2e-746d-4428-825f-4cba057eb62b","name":"todo","color":"green"}]}
            "Tags": {"multi_select": [{"name": tag} for tag in tags]}
        },
        "children": [
            # {
            # 	"object": "block",
            # 	"type": "heading_2",
            # 	"heading_2": {
            # 		"rich_text": [{ "type": "text",
            #                       "text": { "content": head_content} }]
            # 	}
            # },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": txt_content,
                                # "link": txt_content_link
                            }
                        }
                    ]
                }
            }
        ]
    }
    return payload