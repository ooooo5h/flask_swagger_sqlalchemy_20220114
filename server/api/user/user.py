# 사용자에 관련된 기능을 수행하는 파일
# 메쏘드를 만들 때, get/post/put/patch/delete로 만들면, 알아서 메쏘드로 세팅되도록

from tkinter.tix import Tree
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger

from server.model import Users  # users테이블에 연결한 클래스를 가져오기

from server import db  # DB에 INSERT/UPDATE등의 반영을 하기 위한 변수

# 각각의 메쏘드 별로 파라미터를 받아보자

# post메쏘드에서 사용할 파라미터
post_parser = reqparse.RequestParser() # post로 들어오는 파라미터를 확인해볼 변수를 생성
post_parser.add_argument('email', type=str, required=True, location='form')  # 파라미터의 이름/데이터 타입/필수여부/첨부된 곳을 기재해주면 파라미터를 자동으로 가져옴
post_parser.add_argument('password', type=str, required=True, location='form')

# put메쏘드(회원가입)에서 사용할 4가지 파라미터를 추가해보세요
# 변수명은 put_parser에 email, password, name, phone 4가지를 받아주고 전부 string
# put메쏘드에서 실제로 받아서 로그인처럼 로그로만 출력해보자
# swagger문서작업도 진행해보기
put_parser = reqparse.RequestParser()
put_parser.add_argument('email', type=str, required=True, location='form')
put_parser.add_argument('password', type=str, required=True, location='form')
put_parser.add_argument('name', type=str, required=True, location='form')
put_parser.add_argument('phone', type=str, required=True, location='form')

# get메쏘드에서 사용할 파라미터
get_parser = reqparse.RequestParser()
get_parser.add_argument('email', type=str, required=False, location='args')
get_parser.add_argument('name', type=str, required=False, location='args')

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
                # 검색 성공.
                return {
                    'code': 200,
                    'message': '이메일로 사용자 검색 성공',
                    'user': user_by_email.get_data_object()
                }
            else:
                # 검색 실패.
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
            
            # searched_users_list = [ Users(user).get_data_object() for user in users_by_name ] 
            # >>>>> Users(user) 안해도 되네.. 그 이유가 뭐지
            # JSON으로 내려갈 수 있는 dict형태로 목록을 변환시킴
            searched_users_list = [ user.get_data_object() for user in users_by_name ] 
            
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
        
        # 받아낸 파라미터들을 dict 변수에 담아두자
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
        
        if login_user.password == args['password'] :
            # 이메일이 맞는 사용자 中 비밀번호와 파라미터의 비밀번호도 같다 => 로그인 성공 처리
            return{
                'code' : 200,
                'message' : '로그인 성공',
                'data' : {
                    'user' : login_user.get_data_object()
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
        
        # 이미 사용중인 연락처라면, 가입을 불허  =>> 이 코드가 안되는 이유 : 위에서 있으면 return으로 코드를 종료했으니 아래의 코드를 실행할 수 없음
        # if already_email_used.phone == args['phone']:
        #     return{
        #         'code' : 400,
        #         'message' : '이미 사용중인 연락처'
        #     }, 400
        
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
        new_user.password = args['password']
        new_user.name = args['name']
        new_user.phone = args['phone']
        
        # new_user의 객체를 DB에 등록할 준비를 하고 확정짓는 작업하기
        db.session.add(new_user)
        db.session.commit()

        return {
            'code' : 200,
            'message' : '회원가입 성공',
            'data' : {
                'user' : new_user.get_data_object()
            }
        }
    
    @swagger.doc({
        'tags' : ['user'],
        'description' : '회원 탈퇴',
        'parameters' : [
            {
                'name' : 'usre_id',
                'description' : '몇 번 사용자를 지울건가요?',
                'in' : 'query',
                'type' : 'integer',
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
    def delete(self):
        """회원 탈퇴"""
        return {
            '임시' : '회원탈퇴 기능'
        }
    