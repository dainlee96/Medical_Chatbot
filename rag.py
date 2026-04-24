import os
import chromadb
from openai import OpenAI

# OpenAI 클라이언트 초기화 (환경 변수 OPENAI_API_KEY를 자동으로 읽어옴)
client = OpenAI()

# 로컬 하드 디스크에 데이터를 저장하는 ChromaDB 클라이언트 설정
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "medical_knowledge"

# 컬렉션이 없으면 만들고 기초 의료 데이터를 Insert 합니다.
try:
    collection = chroma_client.get_collection(name=collection_name)
except Exception:
    collection = chroma_client.create_collection(name=collection_name)
    # 초기 데모용 의료 데이터셋 추가
    dummy_docs = [
        "두통, 속 메스꺼움, 빛 번짐 현상이 동반된다면 편두통(Migraine)일 확률이 높습니다. 진통제가 듣지 않으면 신경과 방문을 권장합니다.",
        "목이 붓고 침 삼키기가 힘들며 고열이 난다면 편도선염일 수 있습니다. 이비인후과를 방문하세요.",
        "식후 소화 불량, 명치 통증, 잦은 트림과 속 쓰림이 심하다면 위염 또는 위궤양을 의심할 수 있습니다. 내과 방문을 권장합니다.",
        "소변을 볼 때 찌릿한 통증이 있고 잔뇨감이 든다면 방광염일 가능성이 높습니다. 비뇨기과 또는 산부인과에 방문하세요."
    ]
    collection.add(
        documents=dummy_docs,
        metadatas=[{"source": "기본 질병백과"} for _ in dummy_docs],
        ids=[f"doc_{i}" for i in range(len(dummy_docs))]
    )

def get_medical_answer(query: str) -> str:
    """
    실제 Vector DB(ChromaDB)를 검색하고 OpenAI GPT 모델로 답변을 생성하는 함수
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "시스템 오류: OPENAI_API_KEY가 설정되지 않았습니다. 백엔드 환경 변수를 확인해주세요."

    # 1. Vector DB 검색 (사용자 질문과 가장 유사한 문서 1개 추출)
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    # 추출한 문헌 텍스트 조합
    retrieved_docs = results['documents'][0] if results['documents'] else []
    context = "\n".join(retrieved_docs) if retrieved_docs else "관련된 의학 정보가 DB에 존재하지 않습니다."

    # 2. 프롬프트 로드 및 조립
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt_template.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_tmpl = f.read()

    # 프롬프트 템플릿의 빈칸(context, question)을 채워 넣음
    filled_prompt = prompt_tmpl.replace("{context}", context).replace("{question}", query)

    # 3. LLM (OpenAI GPT-3.5-Turbo) 호출
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 항상 환자에게 친절하게 답하는 AI입니다."},
                {"role": "user", "content": filled_prompt}
            ],
            temperature=0.0 # 환각 방지를 위해 창의성 0으로 설정
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}"
