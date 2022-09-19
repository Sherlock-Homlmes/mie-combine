#voice channel name
def channel_name(name):
  global name_check

  kq = "-"
  for i in range(len(name)):
    #print(str(i)+" "+name[i])
    if name[i] in name_check:
      kq = kq + name[i].lower()
    elif name[i] == " " and name[i-1] !=" " and kq[len(kq)-1] != "-":
        kq = kq + "-"

  if kq == "" or kq == "-":
    kq = "room"
  
  else:
    #xử lý tên sau khi lấy
    while kq[len(kq)-1]=="-":
      if kq == "" or kq == "-":
        kq = "room"
      else:
        kq = kq[:-1:]
    
    i=0
    while kq[i] == "-":
      kq=kq[1::]   

  print(kq)
  return kq

#check avaiable name
ban_word =[
  "đụ","địt","đ ụ","đjt","djt",
  "đm","đmm","cđm","vc","d!t","vkl","vcc","vklm","sml","vclm"
  "loz","lồn","l o z",
  "cẹc","buồi","buoi'","cặc","cặk",
  "đĩ","điếm",
  "cock","dick","pussy","porn","bitch","fuk",
  "đéo","loli"
]

def check_avaiable_name(content):
  msg = content.lower()
  msg = msg.replace(" ", "")
  check = any(ele in msg for ele in ban_word)
  if check == False:
    return True
  else:
    return False

#default_data
vc_value = {
  "cc_id":0,
  "host_id":0,
  "channel_name":""
}
cc_value = {
  "vc_id":0,
  "host_id":0,
  "pos":""
}
user_value={
  "id":0,
  "vc_id":0,
  "cc_id":0,
  "locate":""
}

name_check=["q","w","e","r","t","y","u","i","o","p",
"a","s","d","f","g","h","j","k","l",
"z","x","c","v","b","n","m",

"Q","W","E","R","T","Y","U","I","O","P",
"A","S","D","F","G","H","J","K","L",
"Z","X","C","V","B","N","M",

"0","1","2","3","4","5","6","7","8","9",

"ă","â","đ","ê","ô","ơ","ư",
"á","à","ã","ả","ạ",
"ắ","ằ","ặ","ẵ","ẳ",
"ầ","ấ","ẩ","ẫ","ậ",
"è","ẻ","é","ẽ","ẹ",
"ề","ế","ể","ễ","ệ",
"ồ","ố","ổ","ỗ","ộ",
"ờ","ớ","ở","ỡ","ợ",
"ừ","ứ","ử","ữ","ự",
"í","ì","ĩ","ỉ","ị",
"ỳ","ý","ỵ","ỷ","ỹ",
"ò","ó","õ","ỏ","ọ",
"ù","ú","ũ","ụ","ủ",

"_"]

number = [
"0","1","2","3","4","5","6","7","8","9",
]