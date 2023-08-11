import jwt from 'jsonwebtoken';

var validToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJsYW5ndWFnZSI6ImVuZ2xpc2giLCJpYXQiOjE2MjM0MjI2NDB9.XG03KxVEpEngTyAhsDoD4yBZgxqZjD1PapCEniTVjL6NhqqIQ52ehKBrfg3qMtZs6iZfpmvKC7RW_jcZwiaPfUopcoPaS6nhn_ByaptjAZTVXrhvDbk49JhdU6WgNO7xb15D_0-tUiZLG8QNeo-yRwmVYPE2UjKO4uPO_VQYxr4"
var publicKey = `-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCRaHtUpvSkcf2KCwXTiX48Tjxf
bUVFn7YimqGPQbwTnE0WfR5SxLK/DH0os9jCCeb7pJ08AbHFBzQNUfbg47xI3aJh
PMdjL/w3iqfc56C7lt59u4TeOYc7kguph/GTYDPDZkgtbkFJmbkbg9MvV723U1PW
M7N2P4b2Xf3p7ZtaewIDAQAB
-----END PUBLIC KEY-----`
jwt.verify(validToken, publicKey);

// var header = '{"typ":"JWT","alg":"RS256"}'
// var body = '{"language":"english","iat":1623422640}'
// var header = '{"typ":"JWT","alg":"HS256"}'
// var body = '{"language":"english","iat":1623422640}'
// var token = btoa(header) + '.' + btoa(body) + '.';

var forgedToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsYW5ndWFnZSI6ImZsYWcudHh0IiwiaWF0IjoxNjIzNDIyNjQwfQ.fFvgL3eQzCvro2JaoTmhVoXwgVp9svHpmh/pAc+yDiU';

jwt.verify(forgedToken, publicKey);
