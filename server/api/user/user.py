# 사용자에 관련된 기능을 수행하는 파일
# 메쏘드를 만들 때, get/post/put/patch/delete로 만들면, 알아서 메쏘드로 세팅되도록

from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger

from server.model import Users  # users테이블에 연결한 클래스를 가져오기

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

class User(Resource):
    
    @swagger.doc({
        'tags' : ['user'],  # 어떤 종류의 기능인지 분류
        'description' : '사용자 정보 조회',
        'parameters' : [
            # dict로 파라미터들 명시
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


        # email과 비밀번호가 동일한 사람이 있는지 찾아보자 => (SELECT문 + WHERE절 사용)
        
        # 여러단계의 필터를 세팅하고 first() 한번에 호출
        # filter 함수는 여러 줄 적는 경우가 많다 => \ 이용, 코드를 보기좋게 정리하자
        login_user = Users.query\
            .filter(Users.email == args['email'])\
            .filter(Users.password == args['password'])\
            .first()  # 쿼리 수행 결과중 첫줄

        if login_user :
            # 로그인에 성공한 사용자의 데이터도 내려주자
            return{
                'code' : 200,
                'message' : '로그인 성공',
                'data' : {
                    'user' : login_user.get_data_object()
                }
            }
        else :
            return{
                'code' : 400,
                'message' : '로그인 실패',
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
        print(f"이메일 : {args['email']}")
        print(f"비밀번호 : {args['password']}")
        print(f"이름 : {args['name']}")
        print(f"연락처 : {args['phone']}")
        
        return {
            '임시' : '회원가입 기능'
        }
    
