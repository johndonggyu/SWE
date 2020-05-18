from django.shortcuts import render, redirect
import pymysql
from django.http import HttpResponse, JsonResponse
from config import settings
from datetime import datetime

# mysql initialize
connection = pymysql.connect(host='localhost', user ='root', password ='root' ,db ='app')
cursor = connection.cursor()
# Create your views here.
def checksession(req):
	try:
		if req.session['userid'] is None:
			return 0
		else:
			return 1
	except:
		return 0

def index(req):
	try:
		if req.session['userid'] is None:
			return redirect('/login')
		else:
			return render(req, 'index.html', {'userid':req.session['userid']})
	except Exception as e:
		return redirect('/login')	

def enroll(req, gid):
	_userid = req.session['userid']
	_gid = gid
	sql = "insert into member_table values (NULL, (select groupid from group_table where groupid=%s),(select userid from user_table where userid=%s),'waiting')"
	if cursor.execute(sql, (_gid, _userid)):
		connection.commit()
		return HttpResponse('success')
	else:
		return HttpResponse('error')

def main(req):
	if not checksession(req):
		return redirect('/login/')

	sql = "select groupid,theme,area,group_startdate,group_location,group_location2,group_title,group_details,group_owner from group_table"
	chk = cursor.execute(sql)
	rows = cursor.fetchall()
	row_headers = [x[0] for x in cursor.description]
	row_headers.append('status') # 가입했는지,신청중인지,가입안했는지 구분

	group_data = []
	for result in rows:
		# 그룹장인지 검사
		sql = "select count(*) from group_table where group_owner=%s and groupid=%s"
		cursor.execute(sql, (req.session['userid'], result[0]))
		a = cursor.fetchone()
		if a[0] > 0: #그룹장이 맞음
			result = result + ('allowed', )
		elif a[0] < 1: #그룹장이 아닐경우
			# 멤버목록에 allowed 상태일 경우
			sql = "select count(*) from group_table as g inner join member_table as m on g.groupid=m.groupid where m.groupid=%s and m.userid=%s and m.stats=%s"
			cursor.execute(sql, (result[0], req.session['userid'], 'allowed'))
			a = cursor.fetchone()
			if a[0] > 0: #멤버가 맞음
				result = result + ('allowed', )
			else:
				sql = "select count(*) from group_table as g inner join member_table as m on g.groupid=m.groupid where m.groupid=%s and m.userid=%s and m.stats=%s"
				cursor.execute(sql, (result[0], req.session['userid'], 'waiting'))
				a = cursor.fetchone()
				if a[0] > 0: # 신청 대기 중인 멤버가 맞음
					result = result + ('waiting', )
				else:
					sql = "select count(*) from group_table as g inner join member_table as m on g.groupid=m.groupid where m.groupid=%s and m.userid=%s and m.stats=%s"
					cursor.execute(sql, (result[0], req.session['userid'], 'kicked'))
					a = cursor.fetchone()
					if a[0] > 0: # 추방당한 멤버가 맞음
						result = result + ('kicked', )
					else: # 가입하지 않은 멤버가 맞음
						result = result + ('none', )
							
		group_data.append(dict(zip(row_headers, result)))

	# status = ['none','waiting','allowed','discard','kicked']
	## 가입한 그룹, 신청 대기 중인 그룹, 가입하지 않은 그룹 구분
	# 가입한 그룹 : 그룹장이거나 멤버목록에 allowed 상태의 그룹)
	# 신청대기중인 그룹 : 그룹장이 아니고, 멤버목록에 waiting 상태의 그룹)
	# 가입하지않은 그룹 : 그룹장이 아니고, 멤버목록에 없는 그룹)

	if chk == 0:
		return render(req, 'main.html', {'group_list':group_data, 'error':1})
	else:
		return render(req, 'main.html', {'group_list':group_data})

def search(req, kwd):
	keyword = kwd.strip()
	sql = "select groupid,theme,area,group_startdate,group_location,group_location2,group_title,group_details,group_owner from group_table where theme like %s or area like %s or group_startdate like %s or group_location like %s or group_location2 like %s or group_title like %s or group_owner like %s or group_details like %s"
	cursor.execute(sql, ("%"+keyword+"%","%"+keyword+"%","%"+keyword+"%","%"+keyword+"%","%"+keyword+"%","%"+keyword+"%","%"+keyword+"%","%"+keyword+"%"))
	rows = cursor.fetchall()
	row_headers = [x[0] for x in cursor.description]
	row_headers.append('status') # 가입했는지,신청중인지,가입안했는지 구분

	group_data = []
	for result in rows:
		# 그룹장인지 검사
		sql = "select count(*) from group_table where group_owner=%s and groupid=%s"
		cursor.execute(sql, (req.session['userid'], result[0]))
		a = cursor.fetchone()
		if a[0] > 0: #그룹장이 맞음
			result = result + ('allowed', )
		elif a[0] < 1: #그룹장이 아닐경우
			# 멤버목록에 allowed 상태일 경우
			sql = "select count(*) from group_table as g inner join member_table as m on g.groupid=m.groupid where m.groupid=%s and m.userid=%s and m.stats=%s"
			cursor.execute(sql, (result[0], req.session['userid'], 'allowed'))
			a = cursor.fetchone()
			if a[0] > 0: #멤버가 맞음
				result = result + ('allowed', )
			else:
				sql = "select count(*) from group_table as g inner join member_table as m on g.groupid=m.groupid where m.groupid=%s and m.userid=%s and m.stats=%s"
				cursor.execute(sql, (result[0], req.session['userid'], 'waiting'))
				a = cursor.fetchone()
				if a[0] > 0: # 신청 대기 중인 멤버가 맞음
					result = result + ('waiting', )
				else:
					sql = "select count(*) from group_table as g inner join member_table as m on g.groupid=m.groupid where m.groupid=%s and m.userid=%s and m.stats=%s"
					cursor.execute(sql, (result[0], req.session['userid'], 'kicked'))
					a = cursor.fetchone()
					if a[0] > 0: # 추방당한 멤버가 맞음
						result = result + ('kicked', )
					else: # 가입하지 않은 멤버가 맞음
						result = result + ('none', )
							
		group_data.append(dict(zip(row_headers, result)))

	return JsonResponse(group_data, safe=False)

def handle_uploaded_file(f, fname):
	#print(settings.GRPIMG_ROOT+fname)
	#print(fname)
	with open(settings.GRPIMG_ROOT+fname, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

def handle_uploaded_file2(f, fname):
	#print(settings.GRPIMG_ROOT+fname)
	#print(fname)
	with open(settings.GRPPRT_ROOT+fname, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

def create(req):
	if not checksession(req):
		return redirect('/login/')

	if req.method=='POST':
		userid = req.session['userid']
		title = req.POST['gtitle']
		theme = req.POST['gtheme'].strip()
		area = req.POST['garea'].strip()
		start = req.POST['gstartdate'].strip()
		due = req.POST['gduedate']
		loc1 = req.POST['glocation']
		loc2 = req.POST['glocation2']
		detail = req.POST['gdetails']

		_file  = req.FILES['gimage']
		allowed = ['.bmp','.jpg','.jpeg','.png']
		if not fname.endswith(tuple(allowed)):
			result = 2
			return render(req, 'main.html', {'result':result})

		sql = "select max(groupid)+1 from group_table"
		cursor.execute(sql)
		gid = cursor.fetchone()[0]
		if(str(gid) == "None"):
			sql = "alter table group_table auto_increment=1"
			cursor.execute(sql)
			connection.commit()
			img = "1_banner.png"
			gid = 1
		else:
			img = str(gid)+"_banner.png"

		if len(req.FILES['gimage'].name) != 0:
			handle_uploaded_file(req.FILES['gimage'], img)

		sql = "insert into group_table values (NULL,%s,%s,%s,%s,%s,%s,%s,%s, (select userid from user_table where userid=%s))"
		ok = cursor.execute(sql, (theme,area,start,due,loc1,loc2,title,detail,userid))		
		connection.commit()
		if(ok):
			result = '1'
			sql = "insert into member_table values (NULL,%s,%s,%s)"
			cursor.execute(sql, (gid, userid, 'allowed'))
			connection.commit()
		else:
			result = '0'
		return render(req, 'main.html', {'result':result})
	else:
		return render(req, 'main.html')

def mypage(req):
	group_data1 = []
	group_data2 = []
	error1 = 0
	error2 = 0
	if req.method == 'GET':
		if not checksession(req):
			return redirect('/login/')
		sql = "select userid, name, phone, email, alarm from user_table where userid=%s"
		if cursor.execute(sql, (req.session['userid'])):
			rows = cursor.fetchone()
			_userid = rows[0] 
			_name = rows[1]
			_phone = rows[2]
			_email = rows[3]
			_alarm = rows[4]
			myinfo = {
				'userid':_userid,
				'name':_name,
				'phone':_phone,
				'email':_email,
				'alarm':_alarm
			}
		# 마이페이지 - 가입한 그룹
		sql = "select groupid, group_title from group_table where group_owner=%s union select g.groupid, g.group_title from member_table as m inner join group_table as g on m.groupid=g.groupid where m.userid=(select userid from user_table where userid=%s) and stats=%s"
		if cursor.execute(sql, (req.session['userid'], req.session['userid'],'allowed')):
			rows = cursor.fetchall()
			row_headers = [x[0] for x in cursor.description]
			for result in rows:
				group_data1.append(dict(zip(row_headers, result)))
		else:
			error1 = 1
		# 마이페이지 - 신청한 그룹
		sql = "select g.groupid, g.group_title from member_table as m inner join group_table as g on m.groupid=g.groupid where m.userid=(select userid from user_table where userid=%s) and m.stats=%s"
		if cursor.execute(sql, (req.session['userid'],'waiting')):
			rows = cursor.fetchall()
			row_headers = [x[0] for x in cursor.description]
			for result in rows:
				group_data2.append(dict(zip(row_headers, result)))
		else:
			error2 = 1
		return render(req, 'mypage.html', {'myinfo':myinfo, 'group_list1':group_data1, 'group_list2':group_data2,'error1':error1, 'error2':error2})

def leave2(req, groupid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = groupid
	
	# 그룹장이 자기의 그룹에서 탈퇴하는 경우
	sql = "select count(*) from group_table where groupid=%s and group_owner=%s"
	cursor.execute(sql, (_gid, _userid))
	cnt = cursor.fetchone()[0]
	if cnt > 0:
		return HttpResponse('<script>alert("그룹장 이임 후 탈퇴하세요.");document.location.href="/gmain/'+str(_gid)+'/";</script>');
	# 멤버가 자기 그룹에서 탈퇴하는 경우
	sql = "delete from member_table where userid=%s and groupid=%s"
	cursor.execute(sql, (_userid, _gid))
	connection.commit()
	return HttpResponse('<script>alert("탈퇴했습니다.");document.location.href="/main/";</script>')


def leave(req, groupid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = groupid
	
	# 그룹장이 자기의 그룹에서 탈퇴하는 경우
	sql = "select count(*) from group_table where groupid=%s and group_owner=%s"
	cursor.execute(sql, (_gid, _userid))
	cnt = cursor.fetchone()[0]
	if cnt > 0:
		return HttpResponse('그룹장 이임 후 탈퇴하세요.');
	# 멤버가 자기 그룹에서 탈퇴하는 경우
	sql = "delete from member_table where userid=%s and groupid=%s"
	cursor.execute(sql, (_userid, _gid))
	connection.commit()
	return HttpResponse('탈퇴했습니다.')

def myinfo(req):
	if not checksession(req):
		return redirect('/login/')
	if req.method == "POST":
		c_pw = req.POST['change_password1']
		c_phone = req.POST['change_phone']
		c_phone = "".join(filter(str.isdigit, c_phone))
		c_email = req.POST['change_email']
		if len(c_phone) < 10:
			return render(req, 'mypage.html', {'info':'휴대폰 번호를 올바르게 작성해주십시오.'})

		if len(c_pw) < 4:
			# 휴대폰, 이메일만 수정
			sql = "update user_table set email=%s, phone=%s where userid=%s"
			if cursor.execute(sql, (c_email, c_phone, req.session['userid'].strip())):
				connection.commit()
				sql = "select userid, name, phone, email from user_table where userid=%s"
				if cursor.execute(sql, (req.session['userid'])):
					rows = cursor.fetchone()
					_userid = rows[0] 
					_name = rows[1]
					_phone = rows[2]
					_email = rows[3]
					myinfo = {
						'userid':_userid,
						'name':_name,
						'phone':_phone,
						'email':_email
					}
				return render(req, 'mypage.html', {'info':'회원정보가 성공적으로 변경되었습니다.','myinfo':myinfo})
			else:
				return render(req, 'mypage.html', {'info':'변경된 사항이 없습니다.'})
		else:
			# 비밀번호, 휴대폰, 이메일 모두 수정
			sql = "update user_table set passwd=%s, email=%s, phone=%s where userid=%s"
			if cursor.execute(sql, (c_pw, c_email, c_phone, req.session['userid'])):
				connection.commit()
				sql = "select userid, name, phone, email from user_table where userid=%s"
				if cursor.execute(sql, (req.session['userid'])):
					rows = cursor.fetchone()
					_userid = rows[0] 
					_name = rows[1]
					_phone = rows[2]
					_email = rows[3]
					myinfo = {
						'userid':_userid,
						'name':_name,
						'phone':_phone,
						'email':_email
					}
				return render(req, 'mypage.html', {'info':'비밀번호 및 회원정보가 수정되었습니다.','myinfo':myinfo})
			else:
				return render(req, 'mypage.html', {'info':'변경된 사항이 없습니다.'})	
	else:
		return redirect('/mypage/')

def emailalarm(req, tf):
	if not checksession(req):
		return redirect('/login/')
	if tf == 'true':
		tf = True
	elif tf == 'false':
		tf = False
	sql = 'update user_table set alarm=%s where userid=%s'
	if cursor.execute(sql, (tf, req.session['userid'])):
		connection.commit()
		return HttpResponse("이메일 수신 변경됨")

def gsetting(req, gid):
	if not checksession(req):
		return redirect('/login/')
	sql = "select count(*) from group_table where groupid=%s and group_owner=%s"
	if cursor.execute(sql, (gid, req.session['userid'])):
		data = cursor.fetchone()[0]
		if data == 0:
			return redirect('/gmain/'+str(gid)+'/')

	# 공지사항 목록 가져오기
	sql = "select * from notice_table where groupid=%s order by n_date desc"
	if cursor.execute(sql, (gid)):
		rows = cursor.fetchall()
		notice = []
		row_headers = [x[0] for x in cursor.description]
		for row in rows:
			notice.append(dict(zip(row_headers, row)))
	else:
		notice = ();
	return render(req, 'gsetting.html', {'gid':gid, 'notice':notice})

def gset_enrolled(req, gid):
	_userid = req.session['userid']
	_gid = gid
	## 참여중인 멤버 목록
	sql = "select m.userid, u.name from member_table as m inner join user_table as u on m.userid=u.userid where m.groupid=%s and m.stats=%s and u.userid!=%s"
	cursor.execute(sql, (_gid, 'allowed', _userid))
	rows = cursor.fetchall()
	group_data = []
	row_headers = [x[0] for x in cursor.description]
	for row in rows:
		group_data.append(dict(zip(row_headers, row)))
	return JsonResponse(group_data, safe=False)

def gset_joined(req, gid):
	_userid = req.session['userid']
	_gid = gid
	## 가입 신청자 목록
	sql = "select m.userid, u.name from member_table as m inner join user_table as u on m.userid=u.userid where m.groupid=%s and m.stats=%s"
	cursor.execute(sql, (_gid, 'waiting'))
	rows = cursor.fetchall()
	group_data = []
	row_headers = [x[0] for x in cursor.description]
	for row in rows:
		group_data.append(dict(zip(row_headers, row)))
	return JsonResponse(group_data, safe=False)

def accept_users(req, gid, uid):
	_userid = req.session['userid']
	_gid = gid
	_uid = uid
	sql = "update member_table set stats=%s where groupid=%s and userid=%s and stats=%s"
	if cursor.execute(sql, ('allowed', _gid, _uid, 'waiting')):
		connection.commit()
		return HttpResponse('success')
	else:
		return HttpResponse('fail')

def reject_users(req, gid, uid):
	_userid = req.session['userid']
	_gid = gid
	_uid = uid
	sql = "delete from member_table where groupid=%s and userid=%s and stats=%s"
	if cursor.execute(sql, (_gid, _uid, 'waiting')):
		connection.commit()
		return HttpResponse('success')
	else:
		return HttpResponse('fail')

def kick_users(req, gid, uid):
	_userid = req.session['userid']
	_gid = gid
	_uid = uid
	sql = "update member_table set state=%s where groupid=%s and userid=%s and stats=%s"
	if cursor.execute(sql, ('kicked', _gid, _uid, 'allowed')):
		connection.commit()
		return HttpResponse('success')
	else:
		return HttpResponse('fail')

def leave_ownerto_users(req, gid, uid):
	_userid = req.session['userid']
	_gid = gid
	_uid = uid
	sql = "select count(*) from group_table where group_owner=%s and groupid=%s"
	if cursor.execute(sql, (_userid, _gid)):
		if cursor.fetchone()[0] == 1: # 그룹장이라면
			sql = "update group_table set group_owner=%s where groupid=%s"
			if cursor.execute(sql, (_uid, _gid)):
				connection.commit() # 그룹장 이임 끝
				return HttpResponse('그룹장을 '+_uid+'에게 이임했습니다.')
			else:
				return HttpResponse('fail')
		else:
			return HttpResponse('그룹장이 아닙니다.')
	else:
		return HttpResponse('fail')

def save_content(req, gid):
	if not checksession(req):
		return redirect('/login/')
	userid = req.session['userid']
	_gid = gid

	if req.method=='POST':
		title = req.POST['gtitle']
		theme = req.POST['gtheme'].strip()
		area = req.POST['garea'].strip()
		start = req.POST['gstartdate'].strip()
		due = req.POST['gduedate']
		loc1 = req.POST['glocation'].strip()
		loc2 = req.POST['glocation2'].strip()
		detail = req.POST['gdetails']

		img = str(_gid)+"_banner.png"
		#print(req.FILES['gimage'].name)
		if len(req.FILES['gimage'].name) != 0:
			handle_uploaded_file(req.FILES['gimage'], img)

		sql = "update group_table set theme=%s,area=%s,group_startdate=%s,group_duedate=%s,group_location=%s,group_location2=%s,group_title=%s,group_details=%s where group_owner=%s and groupid=%s"
		ok = cursor.execute(sql, (theme,area,start,due,loc1,loc2,title,detail,userid,_gid))		
		if(ok):
			connection.commit()
		return redirect('/gmain/'+str(_gid)+'/')

def load_content(req, gid):
	_userid = req.session['userid']
	_gid = gid
	sql = 'select * from group_table where groupid=%s and group_owner=%s'
	cursor.execute(sql, (_gid, _userid))
	row = cursor.fetchone()
	row_headers = [x[0] for x in cursor.description]
	return JsonResponse(dict(zip(row_headers, row)), safe=False)

def gset_editcontent(req,gid):
	_userid = req.session['userid']
	_gid = gid
	## 그룹 상세 내용 수정
	sql = "select * from group_table where groupid=%s"
	cursor.execute(sql, (_gid))
	rows = cursor.fetchall()
	group_data = []
	row_headers = [x[0] for x in cursor.description]
	for row in rows:
		group_data.append(dict(zip(row_headers, row)))
	return JsonResponse(group_data, safe=False)
	
def gset_noticeadd(req,gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	_gid2 = req.POST['groupid']
	_date = req.POST['date']
	_place = req.POST['place']
	_book = req.POST['book']
	_text = req.POST['text']

	if len(_date) < 1 or len(_place) < 1 or len(_book) < 1:
		return HttpResponse("<script>alert('일정/장소/도서는 입력하여주십시오.');document.location.href='/gsetting/"+str(_gid)+"/';</script>")

	if _gid != int(_gid2):
		return HttpResponse("<script>alert('잘못된 요청입니다.');document.location.href='/main/';</script>")

	if _book == '0' or _book == 0:
		sql = "insert into notice_table values (NULL,%s,%s,%s,NULL,%s)"
	else:
		sql = "insert into notice_table values (NULL,%s,%s,%s,%s,%s)"
	if cursor.execute(sql, (_gid,_date,_place,_book,_text)):
		connection.commit()
		return HttpResponse("<script>alert('공지사항이 추가되었습니다.');document.location.href='/gmain/"+str(_gid)+"/';</script>")
	else:
		return HttpResponse("<script>alert('오류입니다.');document.location.href='/main/';</script>")

	return JsonResponse(group_data, safe=False)

def gmain(req, gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	result = 1
	sql = "select count(*) from member_table where groupid=%s and userid=%s"
	if cursor.execute(sql, (_gid, _userid)):
		row = cursor.fetchone()[0]
		if row == 0:
			return redirect('/main/')

	# 그룹 정보를 가져오자
	sql = "select * from group_table where groupid=%s"
	cursor.execute(sql, (_gid))
	row = cursor.fetchone()
	row_headers = [x[0] for x in cursor.description]
	group_info = dict(zip(row_headers, row))

	sql = "select userid, name from user_table where userid in (select userid from member_table where groupid=%s and stats=%s)"
	cursor.execute(sql, (_gid, 'allowed'))
	#for row in cursor:
	#	print(row[0])
	rows = cursor.fetchall()
	row_header = ['userid','name']
	member_info = []
	for row in rows:
		member_info.append(dict(zip(row_header, row)))
	group_info['member'] = member_info
	#print(group_info)

	# 최근 공지사항 조회
	sql = "select * from notice_table where groupid=%s order by n_date desc limit 1"
	if cursor.execute(sql, (_gid)):
		row = cursor.fetchone()
		row_headers = [x[0] for x in cursor.description]
		notice = dict(zip(row_headers, row))
	if notice['n_date'][6] == '월':
		notice['n_date'] = notice['n_date'][:5]+'0'+notice['n_date'][5:]
	
	group_info['notice'] = notice

	# 최근 공지사항의 발제자 조회
	sql = "select u.userid, u.name from present_table as p inner join user_table as u on p.userid=u.userid where p.groupid=%s and p.noticeid=(select max(p.noticeid) from present_table where p.groupid=%s order by p.noticeid desc) order by p.noticeid desc"
	if cursor.execute(sql, (_gid, _gid)):
		rows = cursor.fetchall()
		row_headers = [x[0] for x in cursor.description]
		presenter = []
		for row in rows:
			presenter.append(dict(zip(row_headers, row)))
		group_info['presenter'] = presenter

	group_info['result'] = result
	return render(req, 'gmain.html', group_info)

def present(req, gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	_file = req.FILES['file']

	fname = _file.name
	allowed = ['.txt','.hwp','.doc','.docx','.ppt','.pptx',
	'.bmp','.jpg','.jpeg','.png','.pdf','.rtf','.tar','.tgz','.xll','.xls',
	'.zip']
	if not fname.endswith(tuple(allowed)):
		# 지원되지 않는 확장자 입니다.
		return HttpResponse('<script>alert("허용되지 않는 확장장입니다.");document.location.href="/gmain/'+str(_gid)+'/";</script>')
	dt = str(datetime.now())
	dtnow = dt[2:4]+dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]+dt[17:19]+dt[20:26]
	fname = str(dtnow) + '_' + _userid + '_' + _file.name

	# 파일 업로드 전, 이전 파일은 삭제하고 올리기
	sql = "select fname from present_table where userid=%s and noticeid=(select noticeid from notice_table where groupid=%s and userid=%s order by noticeid desc limit 1)"
	if cursor.execute(sql, (_userid, _gid, _userid)):
		row = cursor.fetchone()
		sql = "delete from present_table where fname=%s and userid=%s"
		cursor.execute(sql, (row, _userid))
		connection.commit()

	if len(_file.name) != 0:
			handle_uploaded_file2(_file, fname)

	sql = "insert into present_table values (NULL,%s,(select noticeid from notice_table where groupid=%s order by noticeid desc limit 1),%s,%s)"
	if cursor.execute(sql, (_gid, _gid, _userid, fname)):
		connection.commit()
	else:
		return HttpResponse('<script>alert("오류입니다.");document.location.href="/gmain/'+str(_gid)+'/";</script>')

	return HttpResponse('<script>alert("발제자로 신청되었습니다.");document.location.href="/gmain/'+str(_gid)+'/";</script>')

def invite(req, gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	# 예외처리
	sql = "select count(*) from group_table where groupid=%s"
	cursor.execute(sql, (_gid))
	row = cursor.fetchone()[0]
	if row == 0:
		return HttpResponse('<script>alert("없는 그룹입니다.");location.href="/main/";</script>')
	sql = "select count(*) from member_table where groupid=%s and userid=%s"
	cursor.execute(sql, (_gid, _userid))
	row = cursor.fetchone()[0]
	if row == 1:
		return redirect('/main/')
	sql = "insert into member_table values (NULL, (select groupid from group_table where groupid=%s),(select userid from user_table where userid=%s),'waiting')"
	if cursor.execute(sql, (_gid, _userid)):
		connection.commit()
	return redirect('/mypage/', {'alert':'초대가 완료되었습니다. 그룹장의 승인을 기다려주세요.'})

def createvote(req, gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	_title = req.POST['v_title']
	_item1 = req.POST['v_item1']
	_item2 = req.POST['v_item2']
	_item3 = req.POST['v_item3']
	_date = req.POST['v_date']

	if len(_title) < 1 or len(_item1) < 1 or len(_item2) < 1:
		return HttpResponse("<script>alert('최소 항목은 입력하셔야합니다.');document.location.href='/chatting/"+str(_gid)+"/';</script>")

	sql = "select max(voteid)+1 from vote_table"
	cursor.execute(sql)
	row = cursor.fetchone()
	if str(row[0]) == 'None': # 첫번째로 추가되는 거라면
		sql = "insert into vote_table values (1,%s,%s,%s)"
		cursor.execute(sql, (_gid,_title,_date))
		connection.commit()
		sql1 = "insert into vitem_table values (NULL,1,%s,0)"
		sql2 = "insert into vitem_table values (NULL,1,%s,0)"
		sql3 = "insert into vitem_table values (NULL,1,%s,0)"
		cursor.execute(sql1,(_item1))
		cursor.execute(sql2,(_item2))
		cursor.execute(sql3,(_item3))
		connection.commit()
	else:
		sql = "select max(voteid)+1 from vote_table"
		cursor.execute(sql)
		row = cursor.fetchone()
		cnt = int(row[0])
		sql = "insert into vote_table values (%s,%s,%s,%s)"
		cursor.execute(sql, (cnt,_gid,_title,_date))
		connection.commit()
		sql1 = "insert into vitem_table values (NULL,%s,%s,0)"
		sql2 = "insert into vitem_table values (NULL,%s,%s,0)"
		sql3 = "insert into vitem_table values (NULL,%s,%s,0)"
		cursor.execute(sql1,(cnt,_item1))
		cursor.execute(sql2,(cnt,_item2))
		cursor.execute(sql3,(cnt,_item3))
		connection.commit()

	return HttpResponse('<script>alert("투표가 개설되었습니다.");document.location.href="/chatting/'+str(_gid)+'/";</script>')

def chatting(req, gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid

	sql = "select * from message_table where groupid=%s"
	cursor.execute(sql, (_gid))
	rows = cursor.fetchall()
	row_headers = [x[0] for x in cursor.description]
	chat_list = []
	for result in rows:
		chat_list.append(dict(zip(row_headers, result)))
	

	# 투표 목록 불러오기
	sql = "select * from vote_table where groupid=%s"
	cursor.execute(sql, (_gid))
	rows = cursor.fetchall()
	row_headers = [x[0] for x in cursor.description]
	vote_list = []
	for result in rows:
		vote_list.append(dict(zip(row_headers, result)))

	data = {
		'vote_list': vote_list,
		'chat_list': chat_list,
		'gid': _gid,
		'userid': _userid
	}
	return render(req, 'chat.html', data)

def view_items(req, vid):
	if not checksession(req):
		return redirect('/login/')
	_vid = vid
	sql = "select * from vitem_table where voteid=%s"
	cursor.execute(sql, (_vid))
	rows = cursor.fetchall()
	row_headers = [x[0] for x in cursor.description]
	item_list = []
	for row in rows:
		item_list.append(dict(zip(row_headers, row)))
	return JsonResponse(item_list, safe=False)

def voteit(req, gid, vid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	_vid = vid
	_item1 = req.GET['item1']
	_item2 = req.GET['item2']
	_item3 = req.GET['item3']
	if _item1 == '1':
		sql1 = "update vitem_table set vtotal=vtotal+1 where voteid=%s and vitemid=1"
		cursor.execute(sql1, (_vid))
		connection.commit()
	if _item2 == '1':
		sql2 = "update vitem_table set vtotal=vtotal+1 where voteid=%s and vitemid=2"
		cursor.execute(sql2, (_vid))
		connection.commit()
	if _item3 == '1':
		sql3 = "update vitem_table set vtotal=vtotal+1 where voteid=%s and vitemid=3"
		cursor.execute(sql3, (_vid))
		connection.commit()
	return redirect('/main/')

def chat_msg(req, gid):
	if not checksession(req):
		return redirect('/login/')
	_userid = req.session['userid']
	_gid = gid
	_msg = req.GET['msg']
	_date = req.GET['date_t']
	sql = "insert into message_table values (NULL, %s, %s, %s, %s)"
	if cursor.execute(sql, (_gid, _userid, _msg, _date)):
		connection.commit()
		return HttpResponse('success');
	else:
		return HttpResponse('error');

def logout(req):
	del(req.session['userid'])
	return redirect('/login')

def login(req):
	if req.method == "GET":
		try:
			if not req.session['userid']:
				return redirect('/main')
		except Exception as e:
			pass

	if req.method == "POST":
		userid = req.POST['username'].strip()
		passwd = req.POST['password'].strip()

		sql = "select userid,date_format(leave_date, %s) from user_table where userid=(%s) and passwd=(%s)"
		if cursor.execute(sql, ('%Y-%m-%d %H:%i:%s', userid, passwd)):
			row = cursor.fetchone()
			_userid = row[0]
			if str(row[1]) == "None":
				req.session['userid'] = _userid
				return redirect('/main/')
			else:
				_leave_date = row[1]
				return render(req, 'registration/login.html', {'error':'탈퇴한 회원입니다.'})
		else:
			return render(req, 'registration/login.html', {'error':'아이디 또는 비밀번호가 일치하지 않습니다.'})
	else:
		return render(req, 'registration/login.html')

def withdrawl(req):
	if not checksession(req):
		return redirect('/login/')

	sql = "update user_table set leave_date=now() where userid=%s"
	if cursor.execute(sql, (req.session['userid'])):
		connection.commit()
		del(req.session['userid'])
		return render(req, 'registration/login.html', {'error':'회원탈퇴 되었습니다.'})
	else:
		return render(req, 'registration/login.html')

def delete3pass(req):
	sql = 'delete from user_table where leave_date > (now()+INTERVAL 3 DAY)'
	if cursor.execute(sql):
		connection.commit()
		return render(req, 'registration/login.html', {'error':'탈퇴한 지 3일 지난 회원들을 영구삭제하였습니다.'})
	else:
		return render(req, 'registration/login.html', {'error':'삭제할 인원이 없습니다.'})

def register(req):
	if req.method == "POST":
		userid = req.POST['userid'].strip()
		passwd = req.POST['passwd'].strip()
		passwd2 = req.POST['passwd2'].strip()
		name = req.POST['name'].strip()
		tel = req.POST['tel'].strip()
		email = req.POST['email'].strip()

		if passwd != passwd2:
			return render(req, 'registration/register.html', {'status':0})
		else:
			sql = 'insert into user_table values (%s,%s,%s,%s,%s,%s,%s)'
			cursor.execute(sql, (userid,passwd,name,tel,email,0,None))
			connection.commit()
			return redirect('/login/')

	return render(req, 'registration/register.html')

def checkuserid(req):
	userid = req.GET['userid'].strip()
	sql = 'select count(*) from user_table where userid=(%s)'
	cursor.execute(sql, (userid))
	row = cursor.fetchone()
	user_cnt = row[0]
	
	result = {
		'result':'success',
		'data' : 'not exist' if user_cnt == 0 else "exist"
	}
	return JsonResponse(result)

def checkemail(req):
	email = req.GET['email'].strip()
	sql = 'select count(*) from user_table where email=(%s)'
	cursor.execute(sql, (email))
	row = cursor.fetchone()
	email_cnt = row[0]
	
	result = {
		'result':'success',
		'data' : 'not exist' if email_cnt == 0 else "exist"
	}
	return JsonResponse(result)

def findaccount(req):
	if req.method == 'POST':
		find_userid = req.POST['find_userid'].strip()
		find_passwd = req.POST['find_passwd'].strip()
		auth_method = req.POST['auth_method'].strip()
		userid = req.POST['userid'].strip()
		name = req.POST['name'].strip()
		email = req.POST['email'].strip()
		tel = req.POST['tel'].strip()

		# find user id
		if find_userid == '1' and find_passwd == '0':
			# with tel
			if auth_method == 'tel':
				sql = 'select userid from user_table where name=(%s) and phone=(%s)'
				cursor.execute(sql, (name, tel))
				found_userid = cursor.fetchone()[0]
				return render(req, 'registration/findaccount.html', {'found_userid': found_userid})
			# with email
			if auth_method == 'email':
				sql = 'select userid from user_table where name=(%s) and email=(%s)'
				cursor.execute(sql, (name, email))
				found_userid = cursor.fetchone()[0]
				return render(req, 'registration/findaccount.html', {'found_userid': found_userid})
		# find password
		elif find_userid == '0' and find_passwd == '1':
			# with tel
			if auth_method == 'tel':
				sql = 'select passwd from user_table where userid=(%s) and name=(%s) and phone=(%s)'
				cursor.execute(sql, (userid, name, tel))
				found_passwd = cursor.fetchone()[0]
				return render(req, 'registration/findaccount.html', {'found_passwd': found_passwd})
			# with email
			if auth_method == 'email':
				sql = 'select passwd from user_table where userid=(%s) and name=(%s) and email=(%s)'
				cursor.execute(sql, (userid, name, email))
				found_passwd = cursor.fetchone()[0]
				return render(req, 'registration/findaccount.html', {'found_passwd': found_passwd})

		return render(req, 'registration/findaccount.html')
	else:
		return render(req, 'registration/findaccount.html')