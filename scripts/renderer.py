import re

def update_markdown_block(file_path, block_id, new_content):
    """
    Updates the content between <!-- START: AUTO-GEN id=block_id --> and <!-- END: AUTO-GEN -->
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        pattern = f"(<!-- START: AUTO-GEN id={block_id} -->)(.*?)(<!-- END: AUTO-GEN -->)"
        replacement = f"\\1\n{new_content}\n\\3"
        
        new_full_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if content != new_full_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_full_content)
            print(f"Updated block {block_id} in {file_path}")
        else:
            print(f"No changes for block {block_id} in {file_path}")
            
    except Exception as e:
        print(f"Error updating markdown: {e}")
