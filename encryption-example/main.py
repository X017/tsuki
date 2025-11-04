from nacl.public import PrivateKey, Box 


sk_test = PrivateKey.generate()
pk_test = sk_test.public_key


sk_test_2 = PrivateKey.generate()
pk_test_2 = sk_test_2.public_key

test_box = Box(sk_test,pk_test_2)

message = b'hello world'

print(test_box.encrypt(message))
encrypted_message = test_box.encrypt(message)

box_test_2 = Box(sk_test_2,pk_test)

decrypted_message = box_test_2.decrypt(encrypted_message) 
print(decrypted_message.decode('utf-8'))

