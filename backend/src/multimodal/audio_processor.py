from typing import Dict, Any, Optional, List
import asyncio
import base64
import numpy as np
import tempfile
import os

class AudioVideoProcessor:
    def __init__(self):
        self.supported_audio_formats = ['mp3', 'wav', 'ogg', 'm4a']
        self.supported_video_formats = ['mp4', 'avi', 'mov', 'webm']
        self.whisper_available = self._check_whisper()
        self.ffmpeg_available = self._check_ffmpeg()
        
    def _check_whisper(self) -> bool:
        """Whisper 사용 가능 여부 확인"""
        try:
            import whisper
            return True
        except ImportError:
            return False
            
    def _check_ffmpeg(self) -> bool:
        """FFmpeg 사용 가능 여부 확인"""
        try:
            import ffmpeg
            return True
        except ImportError:
            return False
        
    async def process_audio(self, audio_buffer: bytes, options: Dict[str, Any]) -> Dict[str, Any]:
        """오디오 처리 파이프라인"""
        results = {
            'duration': None,
            'format': None,
            'transcript': None,
            'summary': None,
            'analysis': None
        }
        
        # 메타데이터 추출
        results['duration'] = await self.get_audio_duration(audio_buffer)
        results['format'] = options.get('format', 'unknown')
        
        # 음성 인식
        if options.get('transcribe'):
            results['transcript'] = await self.transcribe_audio(audio_buffer)
        
        # 요약 생성
        if options.get('summarize') and results['transcript']:
            results['summary'] = await self.summarize_transcript(results['transcript'])
        
        # 오디오 분석
        if options.get('analyze'):
            results['analysis'] = await self.analyze_audio(audio_buffer)
        
        return results
    
    async def process_video(self, video_buffer: bytes, options: Dict[str, Any]) -> Dict[str, Any]:
        """비디오 처리 파이프라인"""
        results = {
            'metadata': await self.extract_video_metadata(video_buffer),
            'frames': None,
            'audio_track': None,
            'scenes': None
        }
        
        # 키 프레임 추출
        if options.get('extract_frames'):
            results['frames'] = await self.extract_key_frames(video_buffer)
        
        # 오디오 트랙 추출
        if options.get('extract_audio'):
            results['audio_track'] = await self.extract_audio_track(video_buffer)
        
        # 장면 분할
        if options.get('detect_scenes'):
            results['scenes'] = await self.detect_scenes(video_buffer)
        
        return results
    
    async def get_audio_duration(self, audio_buffer: bytes) -> float:
        """오디오 길이 추출 (플레이스홀더)"""
        # 실제 구현에서는 ffprobe 사용
        return 120.5  # 샘플 길이 (초)
    
    async def transcribe_audio(self, audio_buffer: bytes) -> Dict[str, Any]:
        """음성 인식 - Whisper 또는 플레이스홀더"""
        if self.whisper_available:
            return await self._whisper_transcribe(audio_buffer)
        else:
            # 플레이스홀더 구현
            return {
                'text': 'This is a sample transcription of the audio content.',
                'segments': [
                    {'start': 0.0, 'end': 5.2, 'text': 'This is a sample'},
                    {'start': 5.2, 'end': 10.8, 'text': 'transcription of the audio content.'}
                ],
                'language': 'en'
            }
            
    async def _whisper_transcribe(self, audio_buffer: bytes) -> Dict[str, Any]:
        """Whisper를 사용한 실제 음성 인식"""
        import whisper
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_buffer)
            tmp_path = tmp_file.name
        
        try:
            # Whisper 모델 로드 (base 모델)
            model = whisper.load_model('base')
            
            # 전사 실행
            result = model.transcribe(tmp_path)
            
            return {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language']
            }
        finally:
            # 임시 파일 정리
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    async def summarize_transcript(self, transcript: Dict[str, Any]) -> str:
        """전사 내용 요약 (플레이스홀더)"""
        return "Summary: The audio discusses sample content for demonstration purposes."
    
    async def analyze_audio(self, audio_buffer: bytes) -> Dict[str, Any]:
        """오디오 분석 (플레이스홀더)"""
        return {
            'volume_level': 0.75,
            'dominant_frequency': 440,
            'silence_ratio': 0.15,
            'speech_rate': 150  # words per minute
        }
    
    async def extract_video_metadata(self, video_buffer: bytes) -> Dict[str, Any]:
        """비디오 메타데이터 추출 (플레이스홀더)"""
        return {
            'duration': 300.0,
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'codec': 'h264',
            'bitrate': 5000000
        }
    
    async def extract_key_frames(self, video_buffer: bytes, frame_count: int = 3) -> List[Dict[str, Any]]:
        """키 프레임 추출 - FFmpeg 또는 플레이스홀더"""
        if self.ffmpeg_available:
            return await self._ffmpeg_extract_frames(video_buffer, frame_count)
        else:
            # 플레이스홀더 구현
            return [
                {'timestamp': i * 30.0, 'frame_data': f'base64_encoded_frame_{i+1}'}
                for i in range(frame_count)
            ]
            
    async def _ffmpeg_extract_frames(self, video_buffer: bytes, frame_count: int) -> List[Dict[str, Any]]:
        """FFmpeg를 사용한 실제 키 프레임 추출"""
        import ffmpeg
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            tmp_file.write(video_buffer)
            tmp_path = tmp_file.name
        
        try:
            # 비디오 정보 가져오기
            probe = ffmpeg.probe(tmp_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            duration = float(probe['format']['duration'])
            
            frames = []
            for i in range(frame_count):
                timestamp = (duration / frame_count) * i
                
                # 프레임 추출
                out, _ = (
                    ffmpeg
                    .input(tmp_path, ss=timestamp)
                    .output('pipe:', vframes=1, format='rawvideo', pix_fmt='rgb24')
                    .run(capture_stdout=True, quiet=True)
                )
                
                # NumPy 배열로 변환
                frame_array = np.frombuffer(out, np.uint8).reshape([
                    int(video_info['height']),
                    int(video_info['width']),
                    3
                ])
                
                # Base64로 인코딩
                frame_data = base64.b64encode(frame_array.tobytes()).decode()
                
                frames.append({
                    'timestamp': timestamp,
                    'frame_data': frame_data,
                    'width': int(video_info['width']),
                    'height': int(video_info['height'])
                })
            
            return frames
        finally:
            # 임시 파일 정리
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    async def extract_audio_track(self, video_buffer: bytes) -> bytes:
        """비디오에서 오디오 트랙 추출"""
        if self.ffmpeg_available:
            return await self._ffmpeg_extract_audio(video_buffer)
        else:
            return b'extracted_audio_data'
            
    async def _ffmpeg_extract_audio(self, video_buffer: bytes) -> bytes:
        """FFmpeg를 사용한 오디오 트랙 추출"""
        import ffmpeg
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_file:
            video_file.write(video_buffer)
            video_path = video_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
            audio_path = audio_file.name
        
        try:
            # 오디오 추출
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            
            # 추출된 오디오 읽기
            with open(audio_path, 'rb') as f:
                return f.read()
        finally:
            # 임시 파일 정리
            for path in [video_path, audio_path]:
                if os.path.exists(path):
                    os.unlink(path)
    
    async def detect_scenes(self, video_buffer: bytes) -> List[Dict[str, Any]]:
        """장면 분할 - 간단한 구현"""
        # 실제 구현에서는 PySceneDetect 등 사용
        duration = await self.get_video_duration(video_buffer)
        
        # 3등분으로 간단한 장면 분할
        scene_duration = duration / 3
        return [
            {
                'start': 0.0, 
                'end': scene_duration, 
                'description': 'Opening scene',
                'confidence': 0.8
            },
            {
                'start': scene_duration, 
                'end': scene_duration * 2, 
                'description': 'Main content',
                'confidence': 0.9
            },
            {
                'start': scene_duration * 2, 
                'end': duration, 
                'description': 'Conclusion',
                'confidence': 0.7
            }
        ]
        
    async def get_video_duration(self, video_buffer: bytes) -> float:
        """비디오 길이 추출"""
        if self.ffmpeg_available:
            import ffmpeg
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                tmp_file.write(video_buffer)
                tmp_path = tmp_file.name
            
            try:
                probe = ffmpeg.probe(tmp_path)
                return float(probe['format']['duration'])
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            return 180.0  # 기본값