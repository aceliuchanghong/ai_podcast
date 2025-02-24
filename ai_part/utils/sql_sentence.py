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
  wav_remark TEXT,
  cover_remark TEXT,
  task_remark TEXT
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
  wav_remark,
  cover_remark,
  task_remark
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

# select
select_all_url_sql = """
SELECT a.url
FROM ai_podcast_basic_info a
INNER JOIN ai_podcast_detail_info b
    ON a.code = b.code
WHERE b.task_remark = 'upload_suc'
"""

select_max_index_detail_info_sql = """
SELECT MAX(CAST(index_num AS INTEGER))
FROM ai_podcast_detail_info
where task_remark = 'upload_suc'
"""

select_already_up_wav_info_sql = """
SELECT count(*) from ai_podcast_detail_info 
where file_path = ?
and wav_remark = 'upload_suc' 
"""

select_already_up_pic_info_sql = """
SELECT count(*) from ai_podcast_detail_info 
where file_path = ?
and cover_remark = 'upload_suc' 
"""

select_already_gen_wav_info_sql = """
SELECT count(*) from ai_podcast_basic_info 
where code = ?
"""

select_already_gen_wav_detail_sql = """
SELECT a.detail, a.file_path, a.pic_path
FROM ai_podcast_detail_info a
INNER JOIN ai_podcast_basic_info b
    ON a.code = b.code
WHERE b.code = ?
limit 1
"""

# update
update_detail_wav_sql = """
Update ai_podcast_detail_info 
set wav_remark = 'upload_suc' 
where file_path = ?
"""
update_detail_pic_sql = """
Update ai_podcast_detail_info 
set cover_remark = 'upload_suc' 
where file_path = ?
"""
update_detail_task_sql = """
Update ai_podcast_detail_info 
set task_remark = 'upload_suc' 
where code = ?
"""
