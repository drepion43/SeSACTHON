# 채용 이력서 작성 서비스
def profile_check(aiProfile = False):
    '''
    :param
    - aiProfile : bool   # from DB

    :return:
    '''

    if aiProfile:
        # 시니어 프로필 있는 flow
    else:
        # 시니어 프로필 없는 flow


# 자동 매칭 리스트 추천
def jobnotice_self_matching(userId, userProfile):
    '''
    :param
    - userId : str
    - usefProfile : dict
        - certificate : list
        - age : int
        - sex : int (0:male, 1:female)
        - residence : int (0:seoul, 1:busan etc.)
        - major : str
        - career : str

    :return
    - jobNotice : list
        - jobNoticeId : int
        - jobNoticeSubject : string
    '''

    prompt = 'userProfile 리스트와 잘 매칭되는 공고 추천해줘'

    # ?? vectorDB의 경우 데이터를 삭제하기 힘든데 해당부분은 공고를 RDBMS DB에 저장하고 공고를 vectorDB에 주기적으로 업데이트할것인가?

    # rag를 통해 vectorDB에 저장되어있는 공고중 가장 사용자에게 잘 맞는 공고 추천
    jobnotice = rag(userProfile, prompt)

    return jobnotice



# 이력서 작성 페이지 생성
def resume_page_create(jobNoticeId):
    '''
    :param
    - jobNoticeId : int

    :return
    - jobDescriptionBasicList : dict
        - name : str
        - age : int
        - sex : int (0:male, 1:female)
        - addr : str
        - major : str
        - career : str
    '''
    db.connect()
    jobDescriptionBasicList = db.read(jobNoticeId)

    return jobDescriptionBasicList


# 기본 이력서 작성 페이지 작성
def resume_page_write(jobDescriptionBasicList):
    '''
    :param
    - jobDescriptionBasicList : dict
        - name : str
        - age : int
        - sex : int (0:male, 1:female)
        - addr : str
        - major : str
        - career : str
        - resumeText:str
    :return
     - basicListCheck:bool
    '''
    # 리스트 다 작성되었는지
    basicListCheck = False

    # user의 Profile 가져오기 from RDBMS DB
    userProfile = db.read(userId)   # list

    # db를 통해 가져온 userProfile과 jobDescriptionBasicList 매핑
    updateList = dict(jobDescriptionBasicList)
    jobDescriptionBasicList.update(userProfile)

    # 각 key 값이 안들어갔는지 유효성 check
    notUpdateValues = {key: jobDescriptionBasicList[key] for key in jobDescriptionBasicList if key not in userProfile}

    # 없는 값에 대해서는 자기소개 text에서 뽑아 내거나 음성인식 사용
    prompt = '[자기소개 text]에서 [notUpdateValues]에 있는 값이 있는지 확인해주고 해당 값이 없으면 없음으로 답해줘'
    answerChat = openai(prompt, resumeText, notUpdateValues)    # list

    if answerChat == '없음':
        # STT로 질문
        sttAnswer = STT # list 반환
        updateList.update(sttAnswer)
    else:
        updateList.update(answerChat)

    # try catch문으로 문제 발생시 False return
    basicListCheck = True

    return basicListCheck


# 자기소개서 문항 가져오기
def cover_letter_create():
    '''
    :param
    - jobNoticeId : int

    :return
    - jobCoverLetterItem : list
    '''
    db.connect()
    jobCoverLetterItem = db.read(jobNoticeId)

    return jobCoverLetterItem


# 자기소개서 작성 페이지 작성
def cover_letter_write(jobCoverLetterItem):
    '''
    :param
    - jobCoverLetterItem : list
    :return
    - userAnswer:list
    '''
    # 리스트 다 작성되었는지
    answerItemCheck = False

    # user의 자기소개서 가져오기 from RDBMS DB
    userCoverLetter = db.read(userId)   # str

    userAnswer = []
    # 각 문항별로 답변 생성 진행
    for item in jobCoverLetterItem:
        # chatGPT
        itemPrompt = ('[item]에 대한 답변을 진행할거야 나의 자기소개서는 [userCoverLetter]이고 [item]에 대한 적절한 답변을 [item]에'
                      '나와있는 조건으로 답변을 작성해줘 답 할수 없으면 할수 없습니다 라고 답변해줘')

        answer = openai(prompt, item, userCoverLetter)

        if itemPrompt == '할수 없습니다':
            # STT로 문항 질문 및 답변 받아와 정제하여 생성 진행
        userAnswer.append(answer)


    # try catch문으로 문제 발생시 False return
    answerItemCheck = True

    return answerItemCheck


# 자기 소개서 저장
def resume_save(basicListCheck, answerItemCheck):
    '''

    :param
    - basicListCheck: bool
    - answerItemCheck: bool
    :return: bool
    '''

    if not basicListCheck and answerItemCheck:
        # 인적사항 작성으로
        resume_page_write(jobDescriptionBasicList)
    elif basicListCheck and not answerItemCheck:
        # 자기소개 작성으로
        cover_letter_write(jobCoverLetterItem)
    elif not basicListCheck and not answerItemCheck:
        resume_page_write(jobDescriptionBasicList)
        cover_letter_write(jobCoverLetterItem)

    db.save()

    # 저장했는지 확인하는 check point
    return True


