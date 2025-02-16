# create
create_basic_table_sql = """
CREATE TABLE IF NOT EXISTS ai_podcast_basic_info (
  title TEXT, 
  url TEXT,
  code TEXT, 
  remark TEXT
)
"""

create_detail_table_sql = """
CREATE TABLE IF NOT EXISTS ai_podcast_detail_info (
  code TEXT, 
  detail TEXT, 
  file_path TEXT, 
  remark TEXT
)
"""

# insert
insert_basic_info_sql = """
INSERT INTO ai_podcast_basic_info (
  title, 
  url, 
  code, 
  remark
) 
VALUES (?, ?, ?, ?)
"""

insert_detail_info_sql = """
INSERT INTO ai_podcast_detail_info (
  code, 
  detail, 
  file_path, 
  remark
) 
VALUES (?, ?, ?, ?)
"""

# select
select_all_url_sql = """
SELECT url
FROM ai_podcast_basic_info
"""
