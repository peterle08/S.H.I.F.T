# Created & Developed by ...
# Copyright 2021

import string
import random
from datetime import timedelta
from sqlalchemy import func, and_, or_
from app.models import Appointment, Swap, Student, Supervise, Supervisor, Swap, User, Profile, Setting, Role, Employee, Walkin, Shift, Tutor, Course
from app import db

class Function:
    def get_started():
        user = Fetch.user_by_id(1)
        if user == None:
            user = User(username="admin", status="pending", profile_id=1)
            user.set_password("#BestShift2021")
            db.session.add(user)
            db.session.add_all([
                Profile(first_name="admin", last_name="admin", phone="0123456789", email="youremail@example.com"),
                Setting(user_id=1, mode="light"),
                Role(user_id=1, name="admin")
            ])
            db.session.commit()
    
    def validate_username(username):
        if Fetch.user_by_username(username):
            return True
        return False

    def random_password():
        return "mypass:" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 4))

    def verify_password_requirement(password):
        if password.isalnum(): return False
        map = {}    # dictionary that store valid case(s)
        for e in password:
            if e.isdigit() : map["number"] = 1
            else:
                map["alpha"] = 1
                if e.islower(): map["lower"] = 1
                else: map["upper"] = 1
        
        if len(map) < 4: return False
        return True
    
    def is_valid_appointment(student_id, employee_id, start_time, end_time):
        appointment = db.session.query(Appointment)\
                            .filter( and_(
                                        or_(Appointment.employee_id==employee_id, Appointment.student_id==student_id),
                                        or_(Appointment.start_time <= end_time, and_(Appointment.start_time <= start_time, Appointment.end_time >= start_time)))
                            ).first()
        if appointment:
            return False
        return True

    def isWithinDuration(start_time, end_time, current_time):
        if(current_time >= start_time and current_time <= end_time):
            return True
        return False

    def swap_shift(swap):
        requester_shift = Shift.query.filter_by(employee_id=swap.requester_id, date=swap.from_date, start_time=swap.from_time).first()
        accepter_shift = Shift.query.filter_by(employee_id=swap.accepter, date=swap.to_date, start_time=swap.to_time).first()
        requester_shift.employee_id = swap.accepter_id
        accepter_shift.employee_id = swap.requester_id
        db.session.commit()

class Update:
    def password(user, password):   # update password
        user.set_password(password)
        db.session.commit()

    def profile(profile, form):     # update profile 
        profile.first_name = form.first_name.data
        profile.last_name = form.last_name.data
        profile.middle_name = form.middle_name.data
        profile.preferred_name = form.preferred_name.data
        profile.phone = form.phone.data
        profile.email = form.email.data
        profile.address = form.address.data
        profile.city = form.city.data
        profile.state = form.state.data
        profile.zip_code = form.zip_code.data
        db.session.commit()

    def walkin_status(walkin, status):
        walkin.status = status
        db.session.commit()

    def swap_status(swap, status):
        swap.status = status
        db.session.commit()

class Fetch:
    def user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    def user_by_username(username):
        return User.query.filter_by(username=username).first()

    def profile_by_email(email):
        return Profile.query.filter_by(email=email).first()

    def profile_by_profileid(profileid):
        return Profile.query.filter_by(id=profileid).first()

    def user_by_profile(profile_id):
        return User.query.filter_by(profile_id=profile_id).first()

    def shift_for_personal(employee_id):
        return db.session.query(Shift, Profile, Employee)\
                        .join(Employee, Employee.id==Shift.employee_id)\
                        .join(Profile, Profile.id==Employee.profile_id)\
                        .filter(Employee.id==employee_id)\
                        .all()

    def employee_by_profile(profile_id):
        return Employee.query.filter_by(profile_id=profile_id).first()

    # course
    def course_by_id(course_id):
        return Course.query.filter_by(id=course_id).first()
    
    def tutor_availability(department_id, course_id):
        return db.session.query(Shift, Employee, Profile)\
                            .join(Employee, Shift.employee_id==Employee.id)\
                            .join(Tutor, Tutor.employee_id==Employee.id)\
                            .join(Profile, Profile.id==Employee.profile_id)\
                            .filter(Employee.department_id==department_id, Tutor.course_id==course_id)\
                            .order_by(Shift.start_time)\
                            .all()
    def walkin_search(department_id, picked_date):
        return db.session.query(Walkin).filter(and_(func.date(Walkin.time_stamp)==picked_date, Walkin.department_id==department_id))\
                        .order_by(Walkin.time_stamp).all()
    def appointmentby_department(department_id):
        return db.session.query(Appointment)\
                        .join(Employee, Appointment.employee_id==Employee.id)\
                        .filter(Employee.department_id==department_id)\
                        .all()

    def shift_by_supervisor(supervisor_id):
        return db.session.query(Shift, Profile, Employee)\
                        .join(Employee, Employee.id==Shift.employee_id)\
                        .join(Supervise, Supervise.employee_id==Employee.id)\
                        .join(Profile, Profile.id==Employee.profile_id)\
                        .filter(Supervise.supervisor_id==supervisor_id)\
                        .all()
    def shift_for_swap(supervisor_id,role):
        return db.session.query(Shift, Profile, User, Employee)\
                        .join(Employee, Employee.id==Shift.employee_id)\
                        .join(Supervise, Supervise.employee_id==Employee.id)\
                        .join(Profile, Profile.id==Employee.profile_id)\
                        .join(User, User.profile_id==Profile.id)\
                        .join(Role, Role.user_id==User.id)\
                        .filter(Supervise.supervisor_id==supervisor_id, Role.name==role)\
                        .all()
    
    def employee_by_supervisor(supervisor_id):
        return db.session.query(Employee)\
                        .join(Supervise, Supervise.employee_id==Employee.id)\
                        .filter(Supervise.supervisor_id==supervisor_id)\
                        .group_by(Employee.id).all()
    def swap_request_by_supervisor(supervisor_id):
        return db.session.query(Swap)\
                        .join(Employee, Swap.requester_id==Employee.id)\
                        .join(Supervise, Supervise.employee_id==Employee.id)\
                        .filter(Supervise.supervisor_id==supervisor_id, or_(Swap.status=="pending", Swap.status=="accepted"))\
                        .order_by(Swap.from_date).all() 

    def supervise_by_employee(employee_id):
        return Supervise.query.filter_by(employee_id=employee_id).first()


class Insert:
    def appointment(form):
        stmt = Appointment(date=form.date.data, start_time=form.start_time.data, end_time=form.end_time.data, 
                            employee_id=form.employee_id.data, student_id=form.student_id.data, status="booked")
        db.session.add(stmt)
        db.session.commit()

    def schedule(form):
       

        s = set()
        if(form.monday_start.data is None and form.monday_end.data is None):
            s.add(0)
        if(form.tuesday_start.data is None  and form.tuesday_end.data is None):
            s.add(1)
        if(form.wednesday_start.data is None and form.wednesday_end.data is None):
            s.add(2)
        if(form.thursday_start.data is None and form.thursday_end.data is None):
            s.add(3)
        if(form.friday_start.data is None and form.friday_end.data is None):
            s.add(4)

        start_date = form.start_date.data
        end_date = form.end_date.data
        index = start_date

        while index <= end_date:
            if(index.weekday() != 5 and index.weekday() != 6):
                shiftstart = form.monday_start.data
                shiftend = form.monday_end.data
                if(index.weekday() == 0):
                    shiftstart = form.monday_start.data
                    shiftend = form.monday_end.data
                elif(index.weekday() == 1):
                    shiftstart = form.tuesday_start.data
                    shiftend = form.tuesday_end.data
                elif(index.weekday() == 2):
                    shiftstart = form.wednesday_start.data
                    shiftend = form.wednesday_end.data
                elif(index.weekday() == 3):
                    shiftstart = form.thursday_start.data
                    shiftend = form.thursday_end.data
                elif(index.weekday() == 4):
                    shiftstart = form.friday_start.data
                    shiftend = form.friday_end.data
                i = set()
                i.add(index.weekday())
                if(s.issuperset(i) == False):
                    new_shift = Shift(employee_id = form.employee_id.data, date=index, start_time = shiftstart, end_time = shiftend)
                    shifts = Shift.query.filter_by(employee_id = form.employee_id.data, date=index)
                    add = True
                    for shift in shifts:
                        if(Function.isWithinDuration(shift.start_time, shift.end_time,new_shift.start_time)):
                            add = False
                            break
                        elif(Function.isWithinDuration(shift.start_time, shift.end_time,new_shift.end_time)):
                            add=False
                            break
                        elif(Function.isWithinDuration(new_shift.start_time, new_shift.end_time,shift.start_time)):
                            add=False
                            break
                        elif(Function.isWithinDuration(new_shift.start_time, new_shift.end_time,shift.end_time)):
                            add=False
                            break
                    if(add):
                        
                        db.session.add(new_shift)
                        db.session.commit()
            index = index + timedelta(days=1) 
        
    def profile(form):
        stmt = Profile(first_name=form.first_name.data, last_name=form.last_name.data, middle_name=form.middle_name.data,
                        preferred_name=form.preferred_name.data, gender=form.gender.data, phone=form.phone.data, email=form.email.data,
                        address=form.address.data, city=form.city.data, state=form.state.data, zip_code=form.zip_code.data )
        db.session.add(stmt)
        db.session.commit()
    
    def user(username, password, profile_id):
        user = User(username=username, password=password, profile_id=profile_id, status="pending")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    
    def student(id, department_id, profile_id):
        db.session.add(Student(id=id, department_id=department_id, profile_id=profile_id))
        db.session.commit()

    def role(user_id, role):
        db.session.add(Role(user_id=user_id, name=role))
        db.session.commit()
    
    def employee(id, department_id, wage, profile_id):
        db.session.add(Employee(id=id, department_id=department_id, profile_id=profile_id, wage=wage))
        db.session.commit()
    
    def walkin(department_id, student_id, purpose, time_stamp, status, employee_id):
        db.session.add(Walkin(department_id=department_id, student_id=student_id, purpose=purpose,
                                time_stamp=time_stamp, status=status, employee_id=employee_id
                        ))
        db.session.commit()
    def tutor(employee_id, course_id):
        db.session.add(Tutor(employee_id=employee_id, course_id=course_id))
        db.session.commit()
    def supervisor(employee_id):
        db.session.add(Supervisor(id=employee_id))
        db.session.commit()

    def supervise(supervisor_id, employee_id):
        db.session.add(Supervise(supervisor_id=supervisor_id, employee_id=employee_id))
        db.session.commit()    
    def swap_request(form):
        db.session.add(Swap(requester_id=form.requester_id.data, accepter_id=form.accepter_id.data, 
                                        from_date=form.from_date.data, from_time=form.from_time.data,
                                        to_date=form.to_date.data, to_time=form.from_time.data, status="pending"))
        db.session.commit()

class Delete:
    def appointment(date, start_time, student_id)  :
        Appointment.query.filter_by(date=date, start_time=start_time, student_id=student_id).delete()
        db.session.commit()
    def shift(employee_id ,date, start_time):
        Shift.query.filter_by(date=date, start_time=start_time, employee_id=employee_id).delete()
        db.session.commit()