<script>
  import { onMount } from 'svelte';
  import { navigate, Link } from 'svelte-routing';
  import Navbar from '../../components/Navbar.svelte';
  import '@fortawesome/fontawesome-free/css/all.css';
  import { userType } from '../../lib/store';

  const timestamp = new Date().toISOString();

  let currentUserType;

  userType.subscribe(value => {
    currentUserType = value;
  });

  function getIdFromPath() {
    const path = window.location.pathname;
    const segments = path.split('/');
    return segments[segments.length - 1];
  }

  // ================= 공고 정보 ===============================

  let jobid = null;
  let job = null;
  let error = null;

  let title = '';
  let description = '';
  let ageMin = 0;
  let ageMax = 0;
  let additionalProp1 = '';
  let additionalProp2 = '';
  let additionalProp3 = '';

  let createdAt = timestamp;
  let coverLetterQuestions = [];

  // let alertMessage = '';

  // 해당 공고 정보 받아오기
  async function fetchJobDetail(jobid) {
    try {
      const response = await fetch(`http://localhost:8000/job_posting/detail/${jobid}`);
      if (!response.ok) {
        throw new Error('네트워크 응답이 실패했습니다');
      }
      job = await response.json();
      console.log('job ',job);
      title = job.title;
      description = job.description;
      ageMin = job.qualificationsRequired.ageMin;
      ageMax = job.qualificationsRequired.ageMax;
      createdAt = job.createdAt;
      additionalProp1 = job.qualificationsRequired.customQualification.additionalProp1;
      additionalProp2 = job.qualificationsRequired.customQualification.additionalProp2;
      additionalProp3 = job.qualificationsRequired.customQualification.additionalProp3;
      coverLetterQuestions = job.coverLetterQuestions;
      initializeUserAnswers();

      console.log('job title',coverLetterQuestions);

    } catch (err) {
      error = err.message;
      console.log(error);
    }
  }


  // ===================== 지원자 정보 ==========================
  let userID = 'bbbbb';

  let userName = 'kim ha';
  let userAge = 0;
  let userBirth = '';
  let userGender = 0;
  let userProp1 = '';
  let userProp2 = '';
  let userProp3 = '';
  let userSkills = [];
  let userCareers = [];


  let userCoverLetters = [];

  function initializeUserAnswers() {
    userCoverLetters = coverLetterQuestions.map(question => ({
      questionId: question.coverLetterQuestionId,
      answer: ''
    }));
    console.log('Initialized userCoverLetters:', userCoverLetters); // 콘솔 로그로 초기화 확인
  }
  let alertMessage = '';


  //   // 지원자의 정보 가져오기
  // async function fetchUserProfile(id) {
  //   try {
  //     const response = await fetch(`http://localhost:8000/job_posting/detail/${id}`);
  //     if (!response.ok) {
  //       throw new Error('네트워크 응답이 실패했습니다');
  //     }
  //     job = await response.json();
  //     console.log('job ',job);
  //     title = job.title;
  //     description = job.description;
  //     ageMin = job.qualificationsRequired.ageMin;
  //     ageMax = job.qualificationsRequired.ageMax;
  //     createdAt = job.createdAt;
  //     additionalProp1 = job.qualificationsRequired.customQualification.additionalProp1;
  //     additionalProp2 = job.qualificationsRequired.customQualification.additionalProp2;
  //     additionalProp3 = job.qualificationsRequired.customQualification.additionalProp3;
  //     coverLetterQuestions = job.coverLetterQuestions;

  //     console.log('job title',title);

  //   } catch (err) {
  //     error = err.message;
  //     console.log(error);
  //   }
  // }


  function handleRadioChange(event) {
    gender = event.target.value;
    console.log("Selected gender:", gender);
  }

  // 공고 정보 및 지원자 정보 가져오기
  onMount(() => {
    try{
      jobid = getIdFromPath();
      if (jobid != null) {
        console.log('Apply Get Job ID:', jobid);
        fetchJobDetail(jobid);
      }
      console.log('question', coverLetterQuestions);
      // 지원자 정보
      // if (userid != null){

      // }
    } catch (err) {
      error = err.message;
      console.log(error);
    }
  });


  let mediaRecorder;
  let audioBlob = null;

  // ===================전체 녹음=======================
  let totalaudioBlob = null;
  let isTotalRecording = false;

  // 전체 녹음하기 -> audioBlob 생성
  async function totalRecording() {
    try {
      recordedChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        audioBlob = new Blob(recordedChunks, { type: 'audio/webm' });
        console.log("Recording stopped, audioBlob created", audioBlob);
      };

      mediaRecorder.start();
      isTotalRecording = true;
      console.log("Recording started");
    } catch (err) {
      console.error("Error accessing media devices.", err);
      alertMessage = '오디오 장치를 사용할 수 없습니다. 권한을 확인하세요.';
    }
  }

  function stopTotalRecording() {
    mediaRecorder.stop();
    isTotalRecording = false;
    console.log("Recording stopped");
  }

  function toggleTotalRecording() {
    if (isTotalRecording) {
      stopTotalRecording();
    } else {
      totalRecording();
    }
  }

  // 녹음 파일 전송
  async function uploadTotalRecording() {
    if (audioBlob) {
      const formData = new FormData();
      formData.append(job.id, 'user', audioBlob, 'recording.webm');

      try {
        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          alert('파일 업로드 성공');
        } else {
          throw new Error('파일 업로드 실패');
        }
      } catch (err) {
        console.error('Error uploading file:', err);
        alert('파일 업로드 중 오류가 발생했습니다.');
      }
    } else {
      alert('녹음된 오디오가 없습니다.');
    }
    navigate('/home');
  }

  // 제출
  async function handleReumseSubmit() {

    const timestamp = new Date().toISOString();
    console.log('start submit', coverLetterQuestions);
    const resumeSubmitData = {
      userID,
      jobid,
      userCoverLetters,
      createdAt: timestamp,
      updatedAt: timestamp
    };
    console.log("userID", userID);
    console.log("jobid", jobid);
    console.log("userCoverLetters", userCoverLetters);
    console.log("Sucess", resumeSubmitData);
    initializeUserAnswers();
    try {
      const response = await fetch('http://localhost:8000/resume/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(resumeSubmitData)
      });

      if (response.ok) {
        alertMessage = '이력서가 성공적으로 제출되었습니다.';
        // Clear form fields
        userCoverLetters = [];
        
        setTimeout(() => {
          alertMessage = '';
          navigate('/home'); // 변경된 경로 설정
        }, 2000); // 2초 후에 채용 공고 리스트 페이지로 이동
      } else {
        const result = await response.json();
        alertMessage = `작성 실패: ${result.detail}`;
      }
    } catch (error) {
      alertMessage = `작성 실패: 서버 오류 - ${error.message}`;
  }
}

function updateAnswer(index, value) {
    userCoverLetters = userCoverLetters.map((item, i) =>
      i === index ? { ...item, answer: value } : item
    );
  }

</script>

<Navbar />

<main class="container">
  <br><br><br><br><br><br>
  <h1>{job?.title}의 이력서 작성</h1>
  <h4>(녹음 또는 직접 작성 해주세요.)</h4>
  <br><br>
  <h3>전체 녹음</h3>
  <div>
    <button type="button" on:click={toggleTotalRecording} class="record-button">
      <i class="fas fa-microphone"></i> {#if isTotalRecording}녹음 중...{:else}녹음{/if}
    </button>
    <button type="button" on:click={uploadTotalRecording} class="upload-button">
      <i class="fas fa-upload"></i> 녹음 파일로 제출
    </button>
  </div>
  <br><br>
  
  <form on:submit|preventDefault={handleReumseSubmit}>
    <fieldset>
      <label>이름</label>
      <input type="text" bind:value={userName}/>

      <label>나이</label>
      <input type="number" bind:value={userAge} />

      <label>
        생년월일:
        <input type="date" bind:value={userBirth} />
      </label>

      <div class="radio-group">
        <label>남자<input type="radio" name="gender" value=1 on:change={handleRadioChange} />
        </label>
        <label>여자<input type="radio" name="gender" value=0 on:change={handleRadioChange} />
        </label>
      </div>

      <label>학력</label>
      <input type="text" bind:value={userProp1} />
      <label>자격증</label>
      <input type="text" bind:value={userProp2} />
      <!-- <label>경력</label>
      <input type="text" bind:value={userProp3} /> -->
    </fieldset>

    <fieldset>
      <legend>기술</legend>
      {#each userSkills as skill, index}
        <label> 기술 {index + 1}:</label>
          <br>
          <div>
              <input type="text" bind:value={userSkills[index]} placeholder="프로그래밍" required />
          </div>
      {/each}
      <br>
    </fieldset>
  
    <fieldset>
      <legend>경력 사항</legend>
      {#each userCareers as career, index}
        <br>
        <div>
            <label>시작 날짜:</label>
            <input type="date" bind:value={career.startDate} required />

            <label>종료 날짜:</label>
            <input type="date" bind:value={career.endDate} />

            <label>소속:</label>
            <input type="text" bind:value={career.affiliation} required />

            <label>요약:</label>
            <textarea bind:value={career.summary} required></textarea>
        </div>
      {/each}
      <br>
    </fieldset>

    <fieldset>
      <legend>자기 소개서</legend>
      {#each coverLetterQuestions as question, index}
        <br>
        <div>
          <label>질문 {index + 1}:</label>
          <label>{question.content}</label>
          <input type="text" value={userCoverLetters[index]?.answer} on:input={(e) => updateAnswer(index, e.target.value)} required maxlength={question.charLimit} />
        </div>
      {/each}
      <br>
    </fieldset>
    
    <button type="submit">작성</button>
  </form>

</main>


<style>
  .record-button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.2em;
    color: #007bff;
  }

  .record-button .fas {
    margin-right: 5px;
  }

  .record-button:hover {
    color: #0056b3;
  }
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'LotteMartDream', sans-serif;
}

h1 {
    text-align: center;
    margin-bottom: 20px;
    color: #333;
}

.alert {
    color: green;
    margin: 20px 0;
    text-align: center;
}

form {
    display: flex;
    flex-direction: column;
}

label {
    margin-bottom: 10px;
    font-weight: bold;
    color: #333;
}

input, textarea {
    padding: 10px;
    font-size: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 20px;
    width: 100%;
}

textarea {
    resize: vertical;
    height: 100px;
}

button {
    padding: 10px 20px;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    background-color: #007BFF;
    color: white;
    cursor: pointer;
    transition: background 0.3s;
}

button:hover {
    background-color: #0056b3;
}
.radio-group {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    align-items: center;
    margin-left: 320px;
  }
  legend{
    font-weight: bold;
    font-size: 1.2em; /* 글자 크기 조절 */
    color:green;
  }
</style>
  