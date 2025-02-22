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
  index_num TEXT,
  detail TEXT, 
  file_path TEXT, 
  pic_path TEXT,
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
  index_num,
  detail, 
  file_path,
  pic_path,
  remark
) 
VALUES (?, ?, ?, ?, ?, ?)
"""

# select
select_all_url_sql = """
SELECT url
FROM ai_podcast_basic_info
where remark = 'upload_suc'
"""

select_max_index_detail_info_sql = """
SELECT MAX(index_num)
FROM ai_podcast_detail_info
where remark = 'upload_suc'
"""


# update
update_detail_info_sql = """
Update ai_podcast_detail_info 
set remark = 'upload_suc' 
where file_path = ?
"""
