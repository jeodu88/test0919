# 인생 네컷 메모리북 - 추억을 저장하는 웹사이트
import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="주곡중 인생네컷📸",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_filter(image, filter_type):
    """이미지에 필터를 적용하는 함수"""
    if filter_type == "원본":
        return image
    elif filter_type == "흑백":
        return image.convert('L')
    elif filter_type == "세피아":
        # 세피아 톤 효과
        img_array = np.array(image)
        # RGB를 세피아 톤으로 변환
        sepia_matrix = np.array([[0.393, 0.769, 0.189],
                                [0.349, 0.686, 0.168],
                                [0.272, 0.534, 0.131]])
        sepia_img = np.dot(img_array, sepia_matrix.T)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        return Image.fromarray(sepia_img)
    elif filter_type == "블러":
        return image.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_type == "선명화":
        return image.filter(ImageFilter.SHARPEN)
    elif filter_type == "밝게":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.3)
    elif filter_type == "어둡게":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(0.7)
    return image

def create_four_cut_layout(images, filter_type="원본"):
    """4컷 레이아웃을 생성하는 함수"""
    if len(images) < 4:
        # 부족한 이미지는 마지막 이미지로 채움
        while len(images) < 4:
            images.append(images[-1])
    
    # 이미지 크기 조정 (정사각형으로)
    size = 300
    processed_images = []
    
    for img in images[:4]:
        # PIL Image로 변환
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        
        # 정사각형으로 리사이즈
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # 필터 적용
        img = apply_filter(img, filter_type)
        processed_images.append(img)
    
    # 2x2 그리드로 배치
    canvas = Image.new('RGB', (size * 2 + 20, size * 2 + 20), 'white')
    
    positions = [(10, 10), (size + 20, 10), (10, size + 20), (size + 20, size + 20)]
    
    for i, img in enumerate(processed_images):
        canvas.paste(img, positions[i])
    
    return canvas

def main():
    # CSS 스타일링
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .memory-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .upload-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        border: 2px dashed #dee2e6;
    }
    .filter-buttons {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: center;
        margin: 1rem 0;
    }
    .filter-btn {
        background: #6c757d;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .filter-btn:hover {
        background: #495057;
        transform: translateY(-2px);
    }
    .filter-btn.active {
        background: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <h1>📸 인생 네컷 메모리북</h1>
        <p>소중한 추억을 4컷으로 담아보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown("## 🎨 편집 옵션")
        
        # 필터 선택
        filter_options = ["원본", "흑백", "세피아", "블러", "선명화", "밝게", "어둡게"]
        selected_filter = st.selectbox("필터 선택", filter_options)
        
        # 테두리 스타일
        border_style = st.selectbox("테두리 스타일", ["없음", "둥근 모서리", "각진 모서리"])
        
        # 배경색
        bg_color = st.color_picker("배경색", "#ffffff")
        
        st.markdown("---")
        st.markdown("## 💾 저장 옵션")
        save_format = st.selectbox("저장 형식", ["PNG", "JPEG"])
        quality = st.slider("품질", 1, 100, 95)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📷 사진 업로드")
        uploaded_files = st.file_uploader(
            "4장의 사진을 업로드해주세요",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="최대 4장까지 업로드 가능합니다"
        )
        
        if uploaded_files:
            st.success(f"{len(uploaded_files)}장의 사진이 업로드되었습니다!")
            
            # 이미지 미리보기
            st.markdown("### 👀 미리보기")
            for i, uploaded_file in enumerate(uploaded_files[:4]):
                image = Image.open(uploaded_file)
                st.image(image, caption=f"사진 {i+1}", use_container_width=True)
    
    with col2:
        if uploaded_files:
            st.markdown("### ✨ 4컷 결과")
            
            # 이미지 처리
            images = []
            for uploaded_file in uploaded_files[:4]:
                image = Image.open(uploaded_file)
                images.append(image)
            
            # 4컷 레이아웃 생성
            four_cut = create_four_cut_layout(images, selected_filter)
            
            # 결과 표시
            st.image(four_cut, caption="인생 네컷", use_container_width=True)
            
            # 다운로드 버튼
            st.markdown("### 💾 다운로드")
            
            # 이미지를 바이트로 변환
            img_buffer = io.BytesIO()
            if save_format == "PNG":
                four_cut.save(img_buffer, format='PNG')
            else:
                four_cut.save(img_buffer, format='JPEG', quality=quality)
            img_buffer.seek(0)
            
            # 다운로드 링크 생성
            b64 = base64.b64encode(img_buffer.getvalue()).decode()
            href = f'<a href="data:image/{save_format.lower()};base64,{b64}" download="인생네컷.{save_format.lower()}">📥 다운로드</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # 추가 정보
            st.info(f"📏 크기: {four_cut.size[0]}x{four_cut.size[1]}px")
            st.info(f"🎨 필터: {selected_filter}")
    
    # 하단 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>💝 주곡중에서 소중한 순간들을 영원히 간직하세요</p>
        <p>Made with ❤️주곡중❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()