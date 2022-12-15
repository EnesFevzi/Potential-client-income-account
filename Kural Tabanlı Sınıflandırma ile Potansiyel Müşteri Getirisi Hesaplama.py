
#############################################
# Kural Tabanlı Sınıflandırma ile Potansiyel Müşteri Getirisi Hesaplama
#############################################

#############################################
# İş Problemi
#############################################
# Bir oyun şirketi müşterilerinin bazı özelliklerini kullanarak seviye tabanlı (level based) yeni müşteri tanımları (persona)
# oluşturmak ve bu yeni müşteri tanımlarına göre segmentler oluşturup bu segmentlere göre yeni gelebilecek müşterilerin şirkete
# ortalama ne kadar kazandırabileceğini tahmin etmek istemektedir.

# Örneğin: Türkiye’den IOS kullanıcısı olan 25 yaşındaki bir erkek kullanıcının ortalama ne kadar kazandırabileceği belirlenmek isteniyor.


#############################################
# Veri Seti Hikayesi
#############################################
# Persona.csv veri seti uluslararası bir oyun şirketinin sattığı ürünlerin fiyatlarını ve bu ürünleri satın alan kullanıcıların bazı
# demografik bilgilerini barındırmaktadır. Veri seti her satış işleminde oluşan kayıtlardan meydana gelmektedir. Bunun anlamı tablo
# tekilleştirilmemiştir. Diğer bir ifade ile belirli demografik özelliklere sahip bir kullanıcı birden fazla alışveriş yapmış olabilir.

# Price: Müşterinin harcama tutarı
# Source: Müşterinin bağlandığı cihaz türü
# Sex: Müşterinin cinsiyeti
# Country: Müşterinin ülkesi
# Age: Müşterinin yaşı

################# Uygulama Öncesi #####################

#    PRICE   SOURCE   SEX COUNTRY  AGE
# 0     39  android  male     bra   17
# 1     39  android  male     bra   17
# 2     49  android  male     bra   17
# 3     29  android  male     tur   17
# 4     49  android  male     tur   17

################# Uygulama Sonrası #####################

#       customers_level_based        PRICE SEGMENT
# 0   BRA_ANDROID_FEMALE_0_18  1139.800000       A
# 1  BRA_ANDROID_FEMALE_19_23  1070.600000       A
# 2  BRA_ANDROID_FEMALE_24_30   508.142857       A
# 3  BRA_ANDROID_FEMALE_31_40   233.166667       C
# 4  BRA_ANDROID_FEMALE_41_66   236.666667       C


#############################################
# PROJE ADIMLARI
#############################################


# ADIM 1: persona.csv dosyasını okutunuz ve veri seti ile ilgili genel bilgileri gösteriniz.
import pandas as pd
pd.set_option("display.max_rows", None)
df = pd.read_csv('C:/Users/Enes Fevzi/PycharmProjects/pythonProject4/csv/persona.csv')
df.head()
df.shape
df.info()

#  Kaç unique SOURCE vardır? Frekansları nedir?
df["SOURCE"].nunique()
df["SOURCE"].value_counts()

#  Kaç unique PRICE vardır?
df["PRICE"].nunique()

#  Hangi PRICE'dan kaçar tane satış gerçekleşmiş?
df["PRICE"].value_counts()

#  Hangi ülkeden kaçar tane satış olmuş?
df["COUNTRY"].value_counts()
df.groupby("COUNTRY")["PRICE"].count()

df.pivot_table(values="PRICE",index="COUNTRY",aggfunc="count")


#  Ülkelere göre satışlardan toplam ne kadar kazanç
df.groupby("COUNTRY")["PRICE"].sum()
df.groupby("COUNTRY").agg({"PRICE": "sum"})

df.pivot_table(values="PRICE",index="COUNTRY",aggfunc="sum")

#  SOURCE türlerine göre göre satış sayıları
df["SOURCE"].value_counts()

#  Ülkelere göre PRICE ortalamaları
df.groupby(by=['COUNTRY']).agg({"PRICE": "mean"})

#  SOURCE'lara göre PRICE ortalamaları
df.groupby(by=['SOURCE']).agg({"PRICE": "mean"})

#  COUNTRY-SOURCE kırılımında PRICE ortalamaları
df.groupby(by=["COUNTRY", 'SOURCE']).agg({"PRICE": "mean"})



#############################################
# ADIM 2: COUNTRY, SOURCE, SEX, AGE kırılımında ortalama kazançları
#############################################
df.groupby(["COUNTRY", 'SOURCE', "SEX", "AGE"]).agg({"PRICE": "mean"}).head()


#############################################
# ADIM 3: Çıktıyı PRICE'a göre sıralama
#############################################
agg_df = df.groupby(by=["COUNTRY", 'SOURCE', "SEX", "AGE"]).agg({"PRICE": "mean"}).sort_values("PRICE", ascending=False)
agg_df.head()


#############################################
# ADIM 4: Indekste yer alan isimleri değişken ismine çevirelim
#############################################
# Üçüncü sorunun çıktısında yer alan PRICE dışındaki tüm değişkenler index isimleridir.
# Bu isimleri değişken isimlerine çevirelim
# İpucu: reset_index()
# agg_df.reset_index(inplace=True)

agg_df = agg_df.reset_index()
agg_df.head()


#############################################
# ADIM 5: AGE değişkenini kategorik değişkene çeviriniz ve agg_df'e ekleyelim
#############################################
# Age sayısal değişkenini kategorik değişkene çevirelim
# Aralıkları ikna edici olacağını düşündüğünüz şekilde oluşturalım.
# Örneğin: '0_18', '19_23', '24_30', '31_40', '41_70'

# AGE değişkeninin nerelerden bölüneceğini belirtelim:
bins = [0, 18, 23, 30, 40, agg_df["AGE"].max()]

# Bölünen noktalara karşılık isimlendirmelerin ne olacağını ifade edelim:
mylabels = ['0_18', '19_23', '24_30', '31_40', '41_' + str(agg_df["AGE"].max())]

# age'i bölelim:
agg_df["age_cat"] = pd.cut(agg_df["AGE"], bins, labels=mylabels)
agg_df.head()


#############################################
# ADIM 6: Yeni level based müşterileri tanımlayınız ve veri setine değişken olarak ekleyelim
#############################################
# customers_level_based adında bir değişken tanımlayınız ve veri setine bu değişkeni ekleyelim.
# Dikkat!
# list comp ile customers_level_based değerleri oluşturulduktan sonra bu değerlerin tekilleştirilmesi gerekmektedir.
# Örneğin birden fazla şu ifadeden olabilir: USA_ANDROID_MALE_0_18
# Bunları groupby'a alıp price ortalamalarını almak gerekmektedir.

# değişken isimleri:
agg_df.columns

# gözlem değerlerine nasıl erişiriz?
for row in agg_df.values:
    print(row)

# COUNTRY, SOURCE, SEX ve age_cat değişkenlerinin DEĞERLERİNİ yan yana koymak ve alt tireyle birleştirmek istiyoruz.
# Bunu list comprehension ile yapabiliriz.
# Yukarıdaki döngüdeki gözlem değerlerinin bize lazım olanlarını seçecek şekilde işlemi gerçekletirelim:
[row[0].upper() + "_" + row[1].upper() + "_" + row[2].upper() + "_" + row[5].upper() for row in agg_df.values]

# Veri setine ekleyelim:
agg_df["customers_level_based"] = [row[0].upper() + "_" + row[1].upper() + "_" + row[2].upper() + "_" + row[5].upper() for row in agg_df.values]
agg_df.head()

# Gereksiz değişkenleri çıkaralım:
agg_df = agg_df[["customers_level_based", "PRICE"]]
agg_df.head()

for i in agg_df["customers_level_based"].values:
    print(i.split("_"))


# Amacımıza bir adım daha yaklaştık.
# Burada ufak bir problem var. Birçok aynı segment olacak.
# örneğin USA_ANDROID_MALE_0_18 segmentinden birçok sayıda olabilir.
# kontrol edelim:
agg_df["customers_level_based"].value_counts()

# Bu sebeple segmentlere göre groupby yaptıktan sonra price ortalamalarını almalı ve segmentleri tekilleştirmeliyiz.
agg_df = agg_df.groupby("customers_level_based").agg({"PRICE": "mean"})

# customers_level_based index'te yer almaktadır. Bunu değişkene çevirelim.
agg_df = agg_df.reset_index()
agg_df.head()

# kontrol edelim. her bir persona'nın 1 tane olmasını bekleriz:
agg_df["customers_level_based"].value_counts()
agg_df.head()


#############################################
# ADIM 7: Yeni müşterileri (USA_ANDROID_MALE_0_18) segmentlere ayıralım.
#############################################
# PRICE'a göre segmentlere ayırınız,
# segmentleri "SEGMENT" isimlendirmesi ile agg_df'e ekleyiniz,
# segmentleri betimleyiniz,
agg_df["SEGMENT"] = pd.qcut(agg_df["PRICE"], 4, labels=["D", "C", "B", "A"])
agg_df.head(30)
agg_df.groupby("SEGMENT").agg({"PRICE": "mean"})



#############################################
# ADIM 8: Yeni gelen müşterileri sınıflandırınız ne kadar gelir getirebileceğini tahmin edelim
#############################################
# 33 yaşında ANDROID kullanan bir Türk kadını hangi segmente aittir ve ortalama ne kadar gelir kazandırması beklenir?
new_user = "TUR_ANDROID_FEMALE_31_40"
agg_df[agg_df["customers_level_based"] == new_user]

# 35 yaşında IOS kullanan bir Fransız kadını hangi segmente ve ortalama ne kadar gelir kazandırması beklenir?
new_user = "FRA_IOS_FEMALE_31_40"
agg_df[agg_df["customers_level_based"] == new_user]
