# 사용자에 관련된 기능을 수행하는 파일
# 메쏘드를 만들 때, get/post/put/patch/delete로 만들면, 알아서 메쏘드로 세팅되도록
import datetime

from flask import g
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger

from server.api.utils import encode_token, token_required
from server.model import Users  # users테이블에 연결한 클래스를 가져오기

from server import db  # DB에 INSERT/UPDATE등의 반영을 하기 위한 변수

# 각각의 메쏘드 별로 파라미터를 받아보자

# post메쏘드에서 사용할 파라미터
post_parser = reqparse.RequestParser() # post로 들어오는 파라미터를 확인해볼 변수를 생성
post_parser.add_argument('email', type=str, required=True, location='form')  # 파라미터의 이름/데이터 타입/필수여부/첨부된 곳을 기재해주면 파라미터를 자동으로 가져옴
post_parser.add_argument('password', type=str, required=True, location='form')

# put메쏘드에서 사용할 파라미터
put_parser = reqparse.RequestParser()
put_parser.add_argument('email', type=str, required=True, location='form')
put_parser.add_argument('password', type=str, required=True, location='form')
put_parser.add_argument('name', type=str, required=True, location='form')
put_parser.add_argument('phone', type=str, required=True, location='form')

# get메쏘드에서 사용할 파라미터
get_parser = reqparse.RequestParser()
get_parser.add_argument('email', type=str, required=False, location='args')
get_parser.add_argument('name', type=str, required=False, location='args')

# delete메쏘드에서 사용할 파라미터
delete_parser = reqparse.RequestParser()
# delete_parser.add_argument('user_id', type=int, required=True, location='args')

# patch메쏘드에서 사용할 파라미터
patch_parser = reqparse.RequestParser()
patch_parser.add_argument('user_id', type=int, required=True, location='form')
patch_parser.add_argument('field', type=str, required=True, location='form')
patch_parser.add_argument('value', type=str, required=True, location='form')


class User(Resource):
    
    @swagger.doc({
        'tags' : ['user'],  # 어떤 종류의 기능인지 분류
        'description' : '사용자 정보 조회',
        'parameters' : [
            {
                'name': 'email',
                'description': '검색해볼 이메일 - 완전히 맞는 이메일만 찾아줌',
                'in': 'query',
                'type': 'string',
                'required': False
            },
            {
                'name': 'name',
                'description': '검색해볼 이름 - 일부분만 일치해도 찾아줌',
                'in': 'query',
                'type': 'string',
                'required': False
            }
        ],
        'responses' : {
            # 200일때의 응답 예시, 400일때의 예시 등
            '200' : {
                'description' : '사용자 정보 조회 성공!',
            },
            '400' : {
                'description' : '사용자 정보 실패!'
            }
        }
    })
    def get(self):
        """사용자 정보 조회"""
        
        args = get_parser.parse_args()

        # 1. 이메일을 파라미터로 받아서 -> 일치하는 회원 리턴.

        # 이메일 파라미터는 첨부가 안되었을 수도 있다. 실제로 첨부 되었는지 확인하고 동작.
        if args['email']:
            # args : 일종의 dict. => 'email' 조회를 해보면, 첨부가 안되었다면 None으로 리턴.
            # email 파라미터가 첨부 된 상황.

            user_by_email = Users.query.filter(Users.email == args['email']).first()

            if user_by_email:
                return {
                    'code': 200,
                    'message': '이메일로 사용자 검색 성공',
                    'user': user_by_email.get_data_object()
                }
            else:
                return {
                    'code': 400,
                    'message': '이메일 사용자 검색결과 없음'
                }, 400

        # 2. 이름이 파라미터로 왔다면 -> 경진 => 조경진도 리턴. LIKE
        
        if args['name'] : 
            # 이메일은 첨부가 안되어있어야함!! 첨부되어있다면, 위의 if문으로 들어가니까
            # ex. '경' => 조경진/박진경 등 여러 경우가 결과로 나올 수 있다.  == > 검색결과가 1개가 아닌 여러개! => all()
            # 어허라.. 쿼리의 조건에서 LIKE 활용 방법을 알아야겠군
            users_by_name = Users.query.filter(Users.name.like(f"%{args['name']}%")).all()
            
            # JSON으로 내려갈 수 있는 dict형태로 목록을 변환시킴
            searched_users_list = [ user.get_data_object(need_feeds=True) for user in users_by_name ] 
            
            return {
                'code' : 200,
                'message' : '이름으로 사용자 검색 성공',
                'data' : {
                    'users' : searched_users_list,
                }
            }    
        
        return {
            '임시' : '사용자 정보 조회'
        }
  
        
    @swagger.doc({
        'tags' : ['user'], 
        'description' : '로그인',
        'parameters' : [
            {
                'name' : 'email',
                'description' : '로그인에 사용할 이메일 주소',
                'in' : 'formData',  # 문서를 작성할때는 query/formData중에서 택일 (header도 향후 사용할 예정)
                'type' : 'string',  # str아니라 string으로 기재( string/integer/number(float)/boolean 중 택일 (file도 향후 사용할 예정))
                'required' : True,  # 필수 첨부 여부
            },
            {
                'name' : 'password',
                'description' : '로그인에 사용할 비밀번호',
                'in' : 'formData',  
                'type' : 'string',  
                'required' : True,  
            },           
        ],
        'responses' : {
            # 200일때의 응답 예시, 400일때의 예시 등
            '200' : {
                'description' : '로그인 성공',
            },
            '400' : {
                'description' : '아이디 없는 상황'
            }
        }
    })    
    def post(self):
        """로그인"""
        
        args = post_parser.parse_args()

        # 1단계 검사 : 이메일 있나?
        # 통과시 2단계 검사 : 비밀번호도 맞나?
        
        login_user = Users.query\
            .filter(Users.email == args['email'])\
            .first()
            
        if login_user is None:
            return{
                'code' : 400,
                'message' : '이메일 땡'
            }, 400
            
        # login_user가 실제로 있는 상황
        # login_user의 password가 실제로 존재한담 => 파라미터의 패스워드를 비교하기만 하면 됨(DB에 추가 쿼리 조회할 필요 없음)
        
        # login_user.password 기능은 쓸 수가 없음 왜냐!/ 조회할라는 기능은 에러를 발생시키도록 코딩했으니까!
        
        if login_user.verify_password(args['password']) :
            # 이메일이 맞는 사용자 中 비밀번호와 파라미터의 비밀번호도 같다 => 로그인 성공 처리
            return{
                'code' : 200,
                'message' : '로그인 성공',
                'data' : {
                    'user' : login_user.get_data_object(),
                    'token' : encode_token(login_user),
                }
            }
        else :
            # 이메일은 맞는 데 비밀번호가 다름
            return{
                'code' : 400,
                'message' : '비밀번호 땡',
            }, 400
 
    
    @swagger.doc({
        'tags' : ['user'],  
        'description' : '회원가입',
        'parameters' : [
            {
                'name' : 'email',
                'description' : '회원가입에 사용할 이메일 주소',
                'in' : 'formData',  
                'type' : 'string',  
                'required' : True,                     
            },
            {
                'name' : 'password',
                'description' : '회원가입에 사용할 비밀번호',
                'in' : 'formData',  
                'type' : 'string',  
                'required' : True,                     
            },
            {
                'name' : 'name',
                'description' : '사용자 본명',
                'in' : 'formData',  
                'type' : 'string',  
                'required' : True,                     
            },
            {
                'name' : 'phone',
                'description' : '아이디 찾기에 사용할 연락처',
                'in' : 'formData',  
                'type' : 'string',  
                'required' : True,                     
            },                                          
        ],
        'responses' : {
            '200' : {
                'description' : '회원가입 성공!',
            },
            '400' : {
                'description' : '이메일 중복으로 인해 회원 가입 실패'
            }
        }
    })        
    def put(self):
        """회원가입"""
        
        args = put_parser.parse_args()   
        
        # 이미 사용중인 이메일이면 400으로 리턴처리
        already_email_used = Users.query\
            .filter(Users.email == args['email'])\
            .first()
            
        if already_email_used:
            return{
                'code' : 400,
                'message' : '이미 사용중인 이메일입니다.'
            }, 400
                
        already_phone_user = Users.query\
            .filter(Users.phone == args['phone'])\
            .first()
                
        if already_phone_user:
            return{
                'code' : 400,
                'message' : '이미 사용중인 연락처',
            }, 400
        
        
        # 파라미터들을 가지고, users테이블의 row로 추가해보자 (INSERT INO -> ORM개념인 SQLAlchemy로)
        
        # 객체지향 : 새로운 데이터를 추가한다? => 새 인스턴스를 만든다라는 뜻
        new_user = Users()
        new_user.email = args['email']
        new_user.password = args['password']   # password라는 변수에 사용자가 입력하면, 알아서 암호화되서 들어가도록 하고싶다.(뒷단에서 암호화하도록)
        new_user.name = args['name']
        new_user.phone = args['phone']
        
        # new_user의 객체를 DB에 등록할 준비를 하고 확정짓는 작업하기
        db.session.add(new_user)
        db.session.commit()

        return {
            'code' : 200,
            'message' : '회원가입 성공',
            'data' : {
                'user' : new_user.get_data_object(),
                'token' : encode_token(new_user),
            }
        }
    
    @swagger.doc({
        'tags' : ['user'],
        'description' : '회원 탈퇴',
        'parameters' : [
            {
                'name' : 'X-Http-Token',
                'description' : '본인 인증용 토큰',
                'in' : 'header',
                'type' : 'string',
                'required' : True,
            }
        ],
        'responses' : {
            '200' : {
                'description' : '삭제 성공'
            },
            '400' : {
                'description' : '삭제 실패'
            }
        }
    })
    @token_required
    def delete(self):
        """회원 탈퇴"""
     
        args = delete_parser.parse_args()
        
        # g.user로 삭제할 사람 받아오기(토큰으로 누군지 확인이 된 상태이기 때문에)
        delete_user = g.user

        # delete_user에 실제 객체가 들어있다. => 활용하자.

        # db.session.delete(delete_user)  # 누구를 삭제할지 명시.
        # db.session.commit() # 실제 삭제 수행 => 이 사용자의 활동 내역도 다 같이 지워야 정상 동작.

        # 실무 : 기존 데이터를 임시 데이터로 변경.
        delete_user.name = '탈퇴회원'
        delete_user.email = 'retired'
        delete_user.password = 'retired'

        delete_user.retired_at = datetime.datetime.utcnow()

        db.session.add(delete_user)
        db.session.commit()
        
        return {
            'code' : 200,
            'message' : '회원 삭제 수행 완료',
            
        }
    

    @swagger.doc({
    'tags' : ['user'],
    'description' : '회원 정보 수정',
    'parameters' : [
        {
            'name' : 'user_id',
            'description' : '몇 번 사용자의 정보를 수정할지?',
            'in' : 'formData',
            'type' : 'integer',
            'required' : True,
        },
        {
            'name' : 'field',
            'description' : '어느 항목을 변경할지? - name/phone 중 하나로 입력해주세요.',
            'in' : 'formData',
            'type' : 'string',    # name / phone 둘 중 하나로 입력받자 => 입력 자체를 제한을 걸자
            'enum' : ['name', 'phone'],
            'required' : True,
        },
        {
            'name' : 'value',
            'description' : '어떤 값으로 변경할지?',
            'in' : 'formData',
            'type' : 'string',    
            'required' : True,
        },
    ],
        'responses' : {
            '200' : {
                'description' : '회원정보 변경 성공'
            },
            '400' : {
                'description' : '회원정보 변경 실패'
            }
        }
    })
    def patch(self):
        """회원정보 수정"""
        
        args = patch_parser.parse_args()
        
        edit_user = Users.query.filter(Users.id == args['user_id']).first()
        
        if not edit_user:
            return{
                'code' : 400,
                'message' : '해당 사용자는 존재하지 않습니다.'
            }, 400
            
        # edit_user에 사용자가 존재한다 
        if args['field'] == 'name':
            edit_user.name = args['value']
            db.session.add(edit_user)
            db.session.commit()
            
            return {
                'code' : 200,
                'message' : '이름 변경에 성공'
            }
            
        elif args['field'] == 'phone':
            edit_user.phone = args['value']
            db.session.add(edit_user)
            db.session.commit()
            
            return {
                'code' : 200,
                'message' : '연락처 변경에 성공'
            }
        
        return{
            'code' : 400,
            'message' : '필드 항목은 name / phone중 하나만 입력하세요.'
        }, 400