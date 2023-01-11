from pathlib import Path
import streamlit as st
import time
import os
from PIL import Image
import subprocess
import redirect as rd

def get_subdirs(b='.'):
    '''
        Returns all sub-directories in a specific Path
    '''
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd):
            result.append(bd)
    return result


def get_detection_folder():
    '''
        Returns the latest folder in a runs\detect
    '''
    return max(get_subdirs(os.path.join('runs', 'detect')), key=os.path.getmtime)


if __name__ == '__main__':
    
    st.title('YOLOv8 Streamlit App')

    source = ("Image", "Video")
    source_index = st.sidebar.selectbox("Select Input type", range(
        len(source)), format_func=lambda x: source[x])

    if source_index == 0:
        uploaded_file = st.sidebar.file_uploader(
            "Load File", type=['png', 'jpeg', 'jpg'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='Loading...'):
                st.sidebar.image(uploaded_file)
                picture = Image.open(uploaded_file)
                picture = picture.save(f'data/images/{uploaded_file.name}')
                source = f'data/images/{uploaded_file.name}'
        else:
            is_valid = False
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Video", type=['mp4'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='Loading...'):
                st.sidebar.video(uploaded_file)
                with open(os.path.join("data", "videos", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                source = f'data/videos/{uploaded_file.name}'
        else:
            is_valid = False

    if is_valid:
        print('valid')
        if st.button('Detect'):
            with rd.stdout:
                st.info(f"Running YOLOV8")
                result = subprocess.run(['yolo', 'task=detect', 'mode=predict', 'model=yolov8n.pt', 'conf=0.25', 'source={}'.format(source)], capture_output=True, text=True)
                try:
                    result.check_returncode()
                    st.info(result.stdout)
                except subprocess.CalledProcessError as e:
                    st.error(result.stderr)
                    raise e
                
            if source_index == 0:
                with st.spinner(text='Preparing Images'):
                    for img in os.listdir(get_detection_folder()):
                        st.image(str(Path(f'{get_detection_folder()}') / img))

                    st.balloons()
            else:
                with st.spinner(text='Preparing Video'):
                    for vid in os.listdir(get_detection_folder()):
                        st.video(str(Path(f'{get_detection_folder()}') / vid))

                    st.balloons()
