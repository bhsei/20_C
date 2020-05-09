from project.models.model import Project,User,SQLAlchemy,Model,File,Record
from project.models import db
from datetime import datetime
# 由model_id返回record
def get_record_detail_by_model(model_id):
    print(model_id)
    record = Record.query.filter_by(model=model_id).first()

    return record