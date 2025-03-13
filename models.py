from datetime import datetime
from app import db

class VideoGeneration(db.Model):
    __tablename__ = 'video_generations'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    avatar_url = db.Column(db.String(500), nullable=False)
    voice = db.Column(db.String(50), nullable=False)
    video_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='processing')  # processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'avatar_url': self.avatar_url,
            'voice': self.voice,
            'video_path': self.video_path,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
