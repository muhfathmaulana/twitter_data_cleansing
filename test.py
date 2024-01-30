import re

# Kalimat contoh
kalimat = "Mau tanya serius ini sm presiden jokowi======= knp yg ada cm islam nusantara,knp tdk ada kristen nusantara,budha,hindu bahkan kong huchu nusantara???',0,0,0,0,0,0,0,0,0,0,0,0"

# Mengganti dua belas koma dari akhir menjadi tab
hasil = re.sub(r'(,[^,]*,){11}(,[^,]*$)', lambda x: '\t' * (x.group().count(',') - 1), kalimat)
print(hasil)