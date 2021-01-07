#-*- coding: utf-8 -*-
from keras.datasets import imdb
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from keras.models import Sequential , Model
import numpy as np
from numpy.testing import assert_allclose
from pyvi import ViTokenizer , ViUtils
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
from tensorflow.keras.models import model_from_json
from underthesea import word_tokenize
import pandas as pd
import re
import string
import io

#Từ điển tích cực, tiêu cực, phủ định
path_nag = 'sentimentAnalysis/sentiment_dicts/nag.txt'
path_not = 'sentimentAnalysis/sentiment_dicts/not.txt'
path_pos = 'sentimentAnalysis/sentiment_dicts/pos.txt'
path_stopword = 'sentimentAnalysis/sentiment_dicts/Stopwords_vi.txt'
with io.open(path_nag, 'r', encoding='UTF-8') as f:
    nag = f.readlines()
nag_list = [n.replace('\n', '') for n in nag]

with io.open(path_pos, 'r', encoding='UTF-8') as f:
    pos = f.readlines()
pos_list = [n.replace('\n', '') for n in pos]
with io.open(path_not, 'r', encoding='UTF-8') as f:
    not_ = f.readlines()
not_list = [n.replace('\n', '') for n in not_]


VN_CHARS_LOWER = u'ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđð'
VN_CHARS_UPPER = u'ẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸÐĐ'
VN_CHARS = VN_CHARS_LOWER + VN_CHARS_UPPER
def no_marks(s):
    __INTAB = [ch for ch in VN_CHARS]
    __OUTTAB = "a"*17 + "o"*17 + "e"*11 + "u"*11 + "i"*5 + "y"*5 + "d"*2
    __OUTTAB += "A"*17 + "O"*17 + "E"*11 + "U"*11 + "I"*5 + "Y"*5 + "D"*2
    __r = re.compile("|".join(__INTAB))
    __replaces_dict = dict(zip(__INTAB, __OUTTAB))
    result = __r.sub(lambda m: __replaces_dict[m.group(0)], s)
    return result
#Xóa stopword
def delete_stopword(text):
    text = word_tokenize(text)
    with open(path_stopword,'r',encoding = 'UTF-8') as f:
            stopword = f.readlines()
    stopword = [i.replace('\n','') for i in stopword]
    for word in text:
        if word in stopword:
            text.remove(word)
    text_ = ""
    for i in range(len(text)):
        text_ += text[i] + " "
    return text_

def normalize_text(text):

        #Remove các ký tự kéo dài: vd
    text = re.sub(r'([A-Z])\1+', lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)
        
        
        #Chuẩn hóa tiếng Việt, xử lý emoj, chuẩn hóa tiếng Anh, thuật ngữ
    replace_list = {
            'òa': 'oà', 'óa': 'oá', 'ỏa': 'oả', 'õa': 'oã', 'ọa': 'oạ', 'òe': 'oè', 'óe': 'oé','ỏe': 'oẻ',
            'õe': 'oẽ', 'ọe': 'oẹ', 'ùy': 'uỳ', 'úy': 'uý', 'ủy': 'uỷ', 'ũy': 'uỹ','ụy': 'uỵ', 'uả': 'ủa',
            'ả': 'ả', 'ố': 'ố', 'u´': 'ố','ỗ': 'ỗ', 'ồ': 'ồ', 'ổ': 'ổ', 'ấ': 'ấ', 'ẫ': 'ẫ', 'ẩ': 'ẩ',
            'ầ': 'ầ', 'ỏ': 'ỏ', 'ề': 'ề','ễ': 'ễ', 'ắ': 'ắ', 'ủ': 'ủ', 'ế': 'ế', 'ở': 'ở', 'ỉ': 'ỉ',
            'ẻ': 'ẻ', 'àk': u' à ','aˋ': 'à', 'iˋ': 'ì', 'ă´': 'ắ','ử': 'ử', 'e˜': 'ẽ', 'y˜': 'ỹ', 'a´': 'á',
            #Quy các icon về 2 loại emoj: Tích cực hoặc tiêu cực
            "👹": "negative", "👻": "positive", "💃": "positive",'🤙': ' positive ', '👍': ' positive ',
            "💄": "positive", "💎": "positive", "💩": "positive","😕": "negative", "😱": "negative", "😸": "positive",
            "😾": "negative", "🚫": "negative",  "🤬": "negative","🧚": "positive", "🧡": "positive",'🐶':' positive ',
            '👎': ' negative ', '😣': ' negative ','✨': ' positive ', '❣': ' positive ','☀': ' positive ',
            '♥': ' positive ', '🤩': ' positive ', 'like': ' positive ', '💌': ' positive ',
            '🤣': ' positive ', '🖤': ' positive ', '🤤': ' positive ', ':(': ' negative ', '😢': ' negative ',
            '❤': ' positive ', '😍': ' positive ', '😘': ' positive ', '😪': ' negative ', '😊': ' positive ',
            '?': ' ? ', '😁': ' positive ', '💖': ' positive ', '😟': ' negative ', '😭': ' negative ',
            '💯': ' positive ', '💗': ' positive ', '♡': ' positive ', '💜': ' positive ', '🤗': ' positive ',
            '^^': ' positive ', '😨': ' negative ', '☺': ' positive ', '💋': ' positive ', '👌': ' positive ',
            '😖': ' negative ', '😀': ' positive ', ':((': ' negative ', '😡': ' negative ', '😠': ' negative ',
            '😒': ' negative ', '🙂': ' positive ', '😏': ' negative ', '😝': ' positive ', '😄': ' positive ',
            '😙': ' positive ', '😤': ' negative ', '😎': ' positive ', '😆': ' positive ', '💚': ' positive ',
            '✌': ' positive ', '💕': ' positive ', '😞': ' negative ', '😓': ' negative ', '️🆗️': ' positive ',
            '😉': ' positive ', '😂': ' positive ', ':v': '  positive ', '=))': '  positive ', '😋': ' positive ',
            '💓': ' positive ', '😐': ' negative ', ':3': ' positive ', '😫': ' negative ', '😥': ' negative ',
            '😃': ' positive ', '😬': ' 😬 ', '😌': ' 😌 ', '💛': ' positive ', '🤝': ' positive ', '🎈': ' positive ',
            '😗': ' positive ', '🤔': ' negative ', '😑': ' negative ', '🔥': ' negative ', '🙏': ' negative ',
            '🆗': ' positive ', '😻': ' positive ', '💙': ' positive ', '💟': ' positive ',
            '😚': ' positive ', '❌': ' negative ', '👏': ' positive ', ';)': ' positive ', '<3': ' positive ',
            '🌝': ' positive ',  '🌷': ' negative ', '🌸': ' positive ', '🌺': ' positive ',
            '🌼': ' positive ', '🍓': ' positive ', '🐅': ' positive ', '🐾': ' positive ', '👉': ' positive ',
            '💐': ' positive ', '💞': ' positive ', '💥': ' positive ', '💪': ' positive ',
            '💰': ' positive ',  '😇': ' positive ', '😛': ' positive ', '😜': ' positive ',
            '🙃': ' positive ', '🤑': ' positive ', '🤪': ' positive ','☹': ' negative ',  '💀': ' negative ',
            '😔': ' negative ', '😧': ' negative ', '😩': ' negative ', '😰': ' negative ', '😳': ' negative ',
            '😵': ' negative ', '😶': ' negative ', '🙁': ' negative ',
            #Chuẩn hóa 1 số sentiment words/English words
            ':))': '  positive ', ':)': ' positive ', 'ô kê':'ok', 'ô kêi': ' ok ', 'okie': ' ok ', ' o kê ': ' ok ',
            'okey': ' ok ', 'ôkê': ' ok ', 'oki': ' ok ', ' oke ':  ' ok ',' okay':' ok ','okê':' ok ',
            ' tks ': u' cám ơn ', 'thks': u' cám ơn ', 'thanks': u' cám ơn ', 'ths': u' cám ơn ', 'thank': u' cám ơn ',
            '⭐': 'star ', '*': 'star ', '🌟': 'star ', '🎉': u' positive ',
            'kg ': u' không ','not': u' không ', u' kg ': u' không ', '"k ': u' không ',' kh ':u' không ','kô':u' không ','hok':u' không ',' kp ': u' không phải ',u' kô ': u' không ', '"ko ': u' không ', u' ko ': u' không ', u' k ': u' không ', 'khong': u' không ', u' hok ': u' không ',
            'he he': ' positive ','hehe': ' positive ','hihi': ' positive ', 'haha': ' positive ', 'hjhj': ' positive ',
            ' lol ': ' negative ',' cc ': ' negative ','cute': u' dễ thương ','huhu': ' negative ', ' vs ': u' với ', 'wa': ' quá ', 'wá': u' quá', 'j': u' gì ', '“': ' ',
            ' sz ': u' cỡ ', 'size': u' cỡ ', u' đx ': u' được ', 'dk': u' được ', 'dc': u' được ', 'đk': u' được ',
            'đc': u' được ','authentic': u' chuẩn chính hãng ',u' aut ': u' chuẩn chính hãng ', u' auth ': u' chuẩn chính hãng ', 'thick': u' positive ', 'store': u' cửa hàng ',
            'shop': u' cửa hàng ', 'sp': u' sản phẩm ', 'gud': u' tốt ','god': u' tốt ','wel done':' tốt ', 'good': u' tốt ', 'gút': u' tốt ',
            'sấu': u' xấu ','gut': u' tốt ', u' tot ': u' tốt ', u' nice ': u' tốt ', 'perfect': 'rất tốt', 'bt': u' bình thường ',
            'time': u' thời gian ', 'qá': u' quá ', u' ship ': u' giao hàng ', u' m ': u' mình ', u' mik ': u' mình ',
            'ể': 'ể', 'product': 'sản phẩm', 'quality': 'chất lượng','chat':' chất ', 'excelent': 'hoàn hảo', 'bad': 'tệ','fresh': ' tươi ','sad': ' tệ ',
            'date': u' hạn sử dụng ', 'hsd': u' hạn sử dụng ','quickly': u' nhanh ', 'quick': u' nhanh ','fast': u' nhanh ','delivery': u' giao hàng ',u' síp ': u' giao hàng ',
            'beautiful': u' đẹp tuyệt vời ', u' tl ': u' trả lời ', u' r ': u' rồi ', u' shopE ': u' cửa hàng ',u' order ': u' đặt hàng ',
            'chất lg': u' chất lượng ',u' sd ': u' sử dụng ',u' dt ': u' điện thoại ',u' nt ': u' nhắn tin ',u' tl ': u' trả lời ',u' sài ': u' xài ',u'bjo':u' bao giờ ',
            'thik': u' thích ',u' sop ': u' cửa hàng ', ' fb ': ' facebook ', ' face ': ' facebook ', ' very ': u' rất ',u'quả ng ':u' quảng  ',
            'dep': u' đẹp ',u' xau ': u' xấu ','delicious': u' ngon ', u'hàg': u' hàng ', u'qủa': u' quả ',
            'iu': u' yêu ','fake': u' giả mạo ', 'trl': 'trả lời', '><': u' positive ',
            ' por ': u' tệ ',' poor ': u' tệ ', 'ib':u' nhắn tin ', 'rep':u' trả lời ',u'fback':' feedback ','fedback':' feedback ',
            #dưới 3* quy về 1*, trên 3* quy về 5*
            '6 sao': ' 5star ','6 star': ' 5star ', '5star': ' 5star ','5 sao': ' 5star ','5sao': ' 5star ',
            'starstarstarstarstar': ' 5star ', '1 sao': ' 1star ', '1sao': ' 1star ','2 sao':' 1star ','2sao':' 1star ',
            '2 starstar':' 1star ','1star': ' 1star ', '0 sao': ' 1star ', '0star': ' 1star ',}
    
    for k, v in replace_list.items():
        text = text.replace(k, v)
    
    # chuyen punctuation thành space
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    text_list = text.split()
    text = ""
    for i in text_list:
        text += i + " "
    text = delete_stopword(text)
    
    # Chuyển thành chữ thường
    text = text.lower()
    text = text.split()
    len_text = len(text)
    for i in range(len_text): 
        cp_text = text[i]
        
        if cp_text in not_list: # Xử lý vấn đề phủ định (VD: áo này chẳng đẹp--> áo này notpos)
            numb_word = 2 if len_text - i - 1 >= 4 else len_text - i - 2
            for j in range(numb_word):
                temp = text [ i + j + 1] + " " + text [ j + i + 2]
                if temp in pos_list:
                    text[i] = 'positive'
                    text[i + j + 1 ] = ''
                    text[i + j + 2 ] = '' 
                if temp in nag_list:
                    text[i] = 'negative'
                    text[i + j + 1 ] = ''
                    text[i + j + 2 ] = ''
    len_text = len(text)
    for i in range(len_text):
        cp_text = text[i]
        cp_text_2 = ""
        if( i + 1 < len_text):
            cp_text_2 = text[i] + " "+ text[i + 1]
        if cp_text in not_list: # Xử lý vấn đề phủ định (VD: áo này chẳng đẹp--> áo này notpos)
            numb_word = 2 if len_text - i - 1 >= 4 else len_text - i - 1
            for j in range(numb_word):
                if text[i + j + 1] in pos_list:
                     text[i] = 'negative'
                     text[i + j + 1] = ''
                if text[i + j + 1] in nag_list:
                        text[i] = 'positive'
                        text[i + j + 1] = ''
        else: #Thêm feature cho những sentiment words (áo này đẹp--> áo này đẹp positive)
            if cp_text in pos_list:
                text.append('positive')
            elif cp_text in nag_list:
                text.append('negative')
            if cp_text_2 in pos_list:
                text.append('positive')
            elif cp_text_2 in nag_list:
                text.append('negative')
    
    text = u' '.join(text)
    #remove nốt những ký tự thừa thãi
    text = text.replace(u'"', u' ') 
    text = text.replace(u'️ ', u'')
    text = text.replace('🏻','')
    text = text.replace(u"'" , u'')
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    text_list = text.split()
    text = ""
    for i in text_list:
        text += i + " "
    return text

class DataSource(object):

    def _load_raw_data(self, filename, is_train=True):

        a = []
        b = []


        regex = 'train_'
        if not is_train:
            regex = 'test_'

        with open(filename, 'r' , encoding = 'UTF-8') as file:
            for line in file:
                if regex in line:
                    b.append(a)
                    a = [line]
                elif line != '\n':
                    a.append(line)
        b.append(a)

        return b[1:]

    def _create_row(self, sample, is_train=True):

        d = {}
        d['id'] = sample[0].replace('\n', '')
        review = ""

        if is_train:
            for clause in sample[1:-1]:
                review += clause.replace('\n', ' ')
                review = review.replace('.', ' ')

            d['label'] = int(sample[-1].replace('\n', ' '))
        else:
            for clause in sample[1:]:
                review += clause.replace('\n', ' ')
                review = review.replace('.', ' ')


        d['review'] = review
        #d['tokenize'] = ViTokenizer.tokenize(review)
        return d

    def load_data(self, filename, is_train=True):

        raw_data = self._load_raw_data(filename, is_train)
        lst = []

        for row in raw_data:
            lst.append(self._create_row(row, is_train))

        return lst

    def no_mark_dataset(self, x_set,y_set):
        X, y = [], []
        for review, label in zip(list(x_set), list(y_set)):
            #Mở rộng trường hợp ko dấu bằng cách remove dấu tiếng Việt
            X.append(no_marks(review))
            y.append(label)
        return X, y

ds = DataSource()
train_data = pd.DataFrame(ds.load_data('sentimentAnalysis/data_clean/train.crash'))
new_data = []

#Thêm mẫu bằng cách lấy trong từ điển Sentiment (nag/pos)
for index,row in enumerate(pos_list):
    new_data.append(['pos'+str(index),'0',row])
    new_data.append(['pos_nomark' + str(index) , '0' , no_marks(row)] )
for index,row in enumerate(nag_list):
    new_data.append(['neg'+str(index),'1',row])
    new_data.append(['neg' + str(index) , '1' , no_marks(row)])

#Thêm review không dấu từ tập review ban đầu
no_mark_review = []
no_mark_label = []
no_mark_review , no_mark_label = ds.no_mark_dataset(train_data['review'],train_data['label'])
no_mark_index = 0
for i , j in zip(no_mark_review , no_mark_label):
  new_data.append(['nomark'+str(no_mark_index), j , i])
  no_mark_index = no_mark_index + 1

new_data = pd.DataFrame(new_data,columns=list(['id','label','review']))

#train_data and test_data  => gom stt , id , label , review 
train_data = train_data.append(new_data)
# chinh sua comments 
train_data['review'] = [ normalize_text(i) for i in train_data['review']] 
# build training vocabulary and get maximum training sentence length
#and total number of words training data
all_training_words = [word for review in train_data['review'] for word in review.split(" ")]
training_sentence_lengths = [len(review) for review in train_data['review']]
TRAINING_VOCAB = sorted(list(set(all_training_words)))
TRAINING_VOCAB_SIZE = len(TRAINING_VOCAB)
MAX_LENGTH= 200

# text to sequences
trunc_type = 'post'
oov_tok = "none"
tokenizer = Tokenizer(num_words = TRAINING_VOCAB_SIZE, lower =True,char_level =False, oov_token = oov_tok)
tokenizer.fit_on_texts(train_data['review'].tolist())
train_word_index = tokenizer.word_index





def load_parameter(model_h5_filename,model_json_filename):
    file_name_h5 =  "sentimentAnalysis/%s" % model_h5_filename
    file_name_json = "sentimentAnalysis/%s" % model_json_filename
    json_file = open(file_name_json,'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    #load weights into new model 
    loaded_model.load_weights(file_name_h5)
    loaded_model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
    return loaded_model

def save_model(load_model,modelname,modelsavename):
    model_json = load_model.to_json()
    print(model_json)
    with open("sentimentAnalysis/%s" % modelname, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    load_model.save_weights("sentimentAnalysis/%s"% modelsavename)
    print("Saved model to disk")
# Tu hoc
def Learn(option,text,evaluate):
    tmp_text = [normalize_text(text)]
    text_rnn = tokenizer.texts_to_sequences(tmp_text)
    text_rnn = pad_sequences(text_rnn,maxlen=MAX_LENGTH,truncating=trunc_type)
    filepath_LSTM = "sentimentAnalysis/modelLTSM.h5"
    filepath_BiLSTM = "sentimentAnalysis/modelBiLSTM.h5"
    filepath_GRU = "sentimentAnalysis/modelGRU.h5"
    if option == 1:
        load_model = load_parameter("modelLSTM.h5","modelLSTM.json")
        checkpoint_LSTM = ModelCheckpoint(filepath_LSTM, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list_LSTM = [checkpoint_LSTM]
        load_model.fit(text_rnn,np.array([evaluate]), epochs=3, batch_size=1, callbacks=callbacks_list_LSTM)
        save_model(load_model,"modelLSTM.json","modelLSTM.h5")
        del load_model
    elif option == 2:
        load_model = load_parameter("modelBiLSTM.h5","modelBiLSTM.json")
        checkpoint_BiLSTM = ModelCheckpoint(filepath_BiLSTM, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list_BiLSTM = [checkpoint_BiLSTM]
        load_model.fit(text_rnn,np.array([evaluate]), epochs=3, batch_size=1, callbacks=callbacks_list_BiLSTM)
        save_model(load_model,"modelBiLSTM.json","modelBiLSTM.h5")
        del load_model
    elif option == 3:
        load_model = load_parameter("modelGRU.h5","modelGRU.json")
        checkpoint_GRU = ModelCheckpoint(filepath_GRU, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list_GRU= [checkpoint_GRU]
        load_model.fit(text_rnn,np.array([evaluate]), epochs=3, batch_size=1, callbacks=callbacks_list_GRU)
        save_model(load_model,"modelGRU.json","modelGRU.h5")
        del load_model

def sentiment_analyse(text,option):
    text = [normalize_text(text)] 
    text_rnn = tokenizer.texts_to_sequences(text)
    text_rnn = pad_sequences(text_rnn , maxlen=MAX_LENGTH , truncating = trunc_type)
    if option == 1:
        load_model = load_parameter("modelLSTM.h5","modelLSTM.json")
    elif option == 2:
        load_model = load_parameter("modelBiLSTM.h5","modelBiLSTM.json")       
    elif option == 3:
        load_model = load_parameter("modelGRU.h5","modelGRU.json")    
    x  = load_model.predict(text_rnn)
    if x < 0.43:
        return 1
    elif x >= 0.43 and x <= 0.58: 
        return 0
    else:
        return -1
       
