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