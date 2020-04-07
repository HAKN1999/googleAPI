#!/usr/bin/env python
# coding: utf-8

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
import os
import os.path
import pprint
import datetime

#date time untuk menentukan expired tugas dan tugas terbaru
today = datetime.datetime.now()
d = today.strftime('%d').replace('0','')
m = today.strftime('%m').replace('0','')
y = today.strftime('%Y')
today_write = today.strftime("%d-%m-%Y")

def google_class_room():
    #check credentials
    scopes = ["https://www.googleapis.com/auth/classroom.courses","https://www.googleapis.com/auth/classroom.coursework.me",
            "https://www.googleapis.com/auth/classroom.rosters","https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/classroom.profile.emails","https://www.googleapis.com/auth/classroom.profile.photos",
    "https://www.googleapis.com/auth/classroom.announcements"
    ]
    credentials = None
    client_json = ""
    token_name = ""
    if os.path.exists('token_class.pkl'):
        with open('token_class.pkl', 'rb') as token:
            credentials = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_7.json', scopes)
        credentials = flow.run_console()

        with open('token_class.pkl', 'wb') as token:
            pickle.dump(credentials, token)

    print"\nauthorization success"

    # run api service 
    service = build('classroom', 'v1', credentials=credentials)

    # cek semua data rest resource: courses
    courses = []
    page_token = None
    resource = [" ","id"]
    course_Ids = [] 

    while True:
        response = service.courses().list(pageToken=page_token,
                                        pageSize=100).execute()
        courses.extend(response.get('courses', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break

    if not courses:
        print 'No courses found.'
    else:
        # ambil id
        for course in courses:
            course_Ids.append(course.get(resource[1]))


    # student submissons
    student_submissions_data = []
    for course_Id in range(0,len(course_Ids)):
        student_submissions_data.append(service.courses().courseWork().studentSubmissions().list(
            courseId=course_Ids[course_Id],
            courseWorkId='-',
            userId="me").execute())

    # ambil courseid
    data={}
    li_course_Id = []
    for index_studentSubmissions in range(0,len(student_submissions_data)):
        #jika nilai dict dari student_submissions_data {}
        if len(student_submissions_data[index_studentSubmissions]) == 0:
            continue
        #aksess key studentSubmissions untuk mencari couseId
        data_studentsubmissons = student_submissions_data[index_studentSubmissions]['studentSubmissions']
        #aksess key courseId
        for data_courseId in data_studentsubmissons:
            course_Id = data_courseId['courseId']
        #tampung data courseId
        li_course_Id.append(course_Id)

    #ambil data nama pengajar
    courseWork_aktif = []
    add_nama_dosen = {}
    #dapatkan clear nama pengajar 
    for index_data_pengajar in range(0,len(li_course_Id)):
        raw_data_teachers = service.courses().teachers().list(courseId=li_course_Id[index_data_pengajar]).execute()
        # aksess key teachers
        data_teachers = raw_data_teachers['teachers']
        for teachers in data_teachers:
            #nama dosen
            dosen = teachers['profile']['name']['fullName']
            # api coursework
            raw_data_courseWork = service.courses().courseWork().list(courseId=li_course_Id[index_data_pengajar]).execute()
            # aksess key courseWork
            for ektrak_list_courseWork in raw_data_courseWork['courseWork']:
                # aksess key dueDate dan key d,m,y
                day = ektrak_list_courseWork['dueDate']['day']
                month = ektrak_list_courseWork['dueDate']['month']
                year = ektrak_list_courseWork['dueDate']['year']

                # cek valid tugas expired 
                if m == str(month):
                    # cek valid tanggal tugas
                    if d <= str(day):
                        # join dosen dengan data dosen
                        add_nama_dosen={'data':
                                            {
                                            'dosen': dosen,
                                            'dataDetail':ektrak_list_courseWork
                                            }
                                    }

                        # convert to json
                        t_jsn = json.dumps(add_nama_dosen,indent=3)
                        courseWork_aktif.append(t_jsn)
                        
                    else:
                        pass
                else:
                    pass
    return courseWork_aktif
    #     studen_assigment = """ss =[]
    # for access_submission in student_submissions_data:
    #     try:
    #         for i in access_submission['studentSubmissions']:
    #             try:
    #                 print i['assignmentSubmission']
    #             except:
    #                 pass
    #     except:
    #         pass
    # """
# buat google task

# buat google calendar 
def main():
    # convert json to object google_class_room
    """
    [u'topicId', u'updateTime', u'submissionModificationMode', u'description', u'title', u'courseId', u'alternateLink', 
    u'creationTime', u'id', u'creatorUserId', u'state', u'materials', u'maxPoints', u'dueDate', u'dueTime', u'workType']
    """
    classRoom = google_class_room()
    for i in classRoom:
        load = json.loads(i)
        nama_dosen = load['data']['dosen'] 
        dead_line = load['data']['dataDetail']['dueDate'].values()
        title_tugas = load['data']['dataDetail']['title']
        tipe_tugas = load['data']['dataDetail']['workType']
        link = load['data']['dataDetail']['alternateLink']
    
        bahan_tugass = load['data']['dataDetail']['materials']
        for bahan in bahan_tugass:
            data_bahan = bahan['driveFile']['driveFile']
            bahan_tugas_title = data_bahan['title']
            bahan_tugas_thumbnail = data_bahan['thumbnailUrl']
            bahan_tugas_alternatelink= data_bahan['alternateLink']
            
            dict_material={'Materi':{
                'Judul Materi':bahan_tugas_title,
                'Materi thumbnailUrl': bahan_tugas_thumbnail,
                'Materi alternatelink': bahan_tugas_alternatelink,
                        }}
            
        output =  """
        Dosen: {nama_dosen}
        DeadLine: {dead_line}
        Judul: {title_tugas}
        Model: {tipe_tugas}
        Materi judul: {bahan_tugas_title}
            |_Materi thumbnailUrl: {bahan_tugas_thumbnail}
            |_Materi alternateLink: {bahan_tugas_alternatelink}
        Link: {link}""".format(nama_dosen=nama_dosen,dead_line=dead_line,
            title_tugas=title_tugas,tipe_tugas=tipe_tugas,link=link,
            bahan_tugas_title=bahan_tugas_title,bahan_tugas_thumbnail=bahan_tugas_thumbnail,
            bahan_tugas_alternatelink=bahan_tugas_alternatelink)
        print output
    print 
if __name__ == "__main__":
    main()