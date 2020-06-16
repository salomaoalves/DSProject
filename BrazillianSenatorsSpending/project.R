setwd('/home/salomao/Desktop/DSProject/BrazilianSenatorsSpending/')

library(readr)
library(stringr)
library(plyr)
library(tidyr)
library(dplyr)
library(ggplot2)
library(grid)
library(gridExtra)

#load data----------------------------------------------------------------------------------------------
df <- read.csv('datasets/2016.csv', sep=',',encoding='ISO-8859-1', header=T, stringsAsFactors=F)
View(df)
str(df)

#DATA MUNGING-------------------------------------------------------------------------------------------

#change the column name to english
df <- rename(df, Year=ANO, Month=MES, Senator=SENADOR, ExpenseType=TIPO_DESPESA,
            EIN_SSN=CNPJ_CPF, Provider=FORNECEDOR, Document=DOCUMENTO, Date=DATA,
            Details=DETALHAMENTO, Refunded=VALOR_REEMBOLSADO)

#find and drop na values
sapply(df, function(x) sum(is.na(x)))
df <- na.omit(df)

#creat a column with the day of the week
df$Date <- as.Date(as.character(df$Date), format = "%d/%m/%Y")
df$dayWeek <- as.character(weekdays(df$Date)) 
days_pt <- c("segunda","terça","quarta","quinta","sexta","sábado","domingo") 
days_en <- c("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
df$dayWeek <- as.factor(mapvalues(df$dayWeek, from=days_pt, to=days_en))

#creat a column with the day
df <- df %>%
  separate(Date, into=c('Useless1','Useless2','Day'), sep='\\-')

#I'll drop out the column Year (same year)
df['Year'] <- NULL
df['Useless1'] <- NULL
df['Useless2'] <- NULL

#transformation some data to type factor
cols <- c('Month','Senator','ExpenseType','Day')
for (i in 1:length(cols)){
  df[,cols[i]] <- as.factor(df[,cols[i]])
}

#change the values in Details to english
namePt <- c("Aluguel de im\xf3veis para escrit\xf3rio pol\xedtico, compreendendo despesas concernentes a eles.",
            "Aquisi\xe7\xe3o de material de consumo para uso no escrit\xf3rio pol\xedtico, inclusive aquisi\xe7\xe3o ou loca\xe7\xe3o de software, despesas postais, aquisi\xe7\xe3o de publica\xe7\xf5es, loca\xe7\xe3o de m\xf3veis e de equipamentos. ",
            "Contrata\xe7\xe3o de consultorias, assessorias, pesquisas, trabalhos t\xe9cnicos e outros servi\xe7os de apoio ao exerc\xedcio do mandato parlamentar",
            "Divulga\xe7\xe3o da atividade parlamentar", "Locomo\xe7\xe3o, hospedagem, alimenta\xe7\xe3o, combust\xedveis e lubrificantes",
            "Passagens a\xe9reas, aqu\xe1ticas e terrestres nacionais", "Servi\xe7os de Seguran\xe7a Privada")
nameEn <- c("Rental of real estate for political office, including expenses related to them.",
            "Purchase of consumables for use in the political office, including purchase or rental of software, postal charges, purchase of publications, rental of furniture and equipment.",
            "Hiring consultancies, advisory services, research, technical works and other services to support the exercise of parliamentary mandate.",
            "Dissemination of parliamentary activity", "Locomotion, lodging, food, fuels and lubricants",
            "National air, water and land tickets", "Private Security Services")
df$ExpenseType <-mapvalues(df$ExpenseType, from=namePt, to=nameEn)

#change some names (later, this will be useful)
df$Senator <- mapvalues(df$Senator, from=c("TELM\xc1RIO MOTA","JO\xc3O CAPIBERIBE","JOS\xc9 MEDEIROS"), 
                        to=c("TELMÁRIO MOTA","JOÃO CAPIBERIBE","JOSÉ MEDEIROS"))

#replace all ',' to '.' in the column Refunded
for (j in 1:nrow(df)){
  for (i in 1:str_length(df[j,'Refunded'])){
    if (str_sub(df[j,'Refunded'],start=i,end=i) == ','){
      str_sub(df[j,'Refunded'],start=i,end=i) = '.'
    }
  }
}

#transformation Refunded to type numeric
df$Refunded <- as.numeric(df[,'Refunded'])

#DATA ANALYSIS AND EXPLORATION--------------------------------------------------------------------------

#resumo estatistico
cols <- c("Month","Senator","Refunded","Day","dayWeek")
rs <- summary(df[,cols])

#frenquecy of spending per...
fs <- textGrob("Frequency of Spending")

data <- df %>%
  count(Senator) %>%
  filter(n>300)
fs1 <- ggplot(data, aes(x=Senator)) + ggtitle("Spend Frequency per Senator (Top 25)") + xlab("Senator") +
  geom_bar(stat = "identity", aes(y=n)) + ylab("Number #") + theme_minimal() + coord_flip()
fs2 <- ggplot(df, aes(Month)) + ggtitle("Spend Frequency per Month") + xlab("Month") +
  geom_histogram(stat = "count", width = 0.5) + ylab("Number #") + theme_minimal()
fs3 <- ggplot(df, aes(x=dayWeek)) + ggtitle("Spend Frequency per Day") + xlab("Day") +
  geom_histogram(stat = "count", width = 0.5) + ylab("Number #") + theme_minimal()

grid.arrange(fs, fs1, fs2, fs3, ncol=2)


#Spend Overrall
so <- textGrob("Spend Overall")

dt <- df %>%
  select(dayWeek,Refunded) %>%
  group_by(dayWeek) %>%
  summarise(Spend = round(sum(Refunded)/1000000,2)) %>%
  arrange(match(dayWeek,c("Monday","Tuesday","Wednesday",
                          "Thursday","Friday","Saturday","Sunday")))
so2 <- ggplot(data=dt, aes(x=dayWeek,y=Spend, group=1)) + ggtitle("Spend Evolution during Days of the Week") + 
  xlab("Day of the Week") + geom_point() + geom_line() + theme_minimal()

dt <- df %>%
  select(Month,Refunded) %>%
  group_by(Month) %>%
  summarise(Spend = round(sum(Refunded)/1000000,2))
so3 <- ggplot(data=dt, aes(x=Month,y=Spend, group=1)) + ggtitle("Spend Evolution during Months") + 
  xlab("Months") + geom_point() + geom_line() + theme_minimal()

dt <- df %>%
  select(ExpenseType,Refunded) %>%
  group_by(ExpenseType) %>%
  summarise(Spend = round(sum(Refunded)/1000000,2)) %>%
  mutate(Legend=factor(c('1','2','3','4','5','6','7')))
so4 <- ggplot(data = dt, aes(x=Legend,y=Spend, group=1)) + ggtitle("Spends per Expense Type") + 
  xlab("Expense Type") + geom_point() + geom_line() + theme_minimal() + 
  legend("top",col=Legend,legend=ExpenseTypeName)
                  #Lembrar de explicar as legendas

grid.arrange(so1, so2, so3, so4, ncol=2)

#Top 10 Spenders
dt <- df %>%
  select(Senator,Refunded) %>%
  group_by(Senator) %>%
  summarise(Spend = round(sum(Refunded)/1000,2)) %>%
  arrange(desc(Spend)) %>% head(10)
g <- ggplot(dt, aes(Senator,Spend)) + ggtitle("Top 10 Spenders") + xlab("Senator") +
  geom_bar(stat="identity") + ylab("R$") + theme_minimal() + coord_flip()
  
#boxplot/vilion to Top 10 Spenders
dt <- df %>%
  select(Senator,Refunded) %>%
  filter(Senator == "PAULO ROCHA" | Senator == "RANDOLFE RODRIGUES" | 
         Senator == "TERLMÁRIO MOTA" | Senator == "ROBERTO ROCHA" | 
         Senator == "JOÃO CAPIBERIBE" | Senator == "FERNANDO BEZERRA COELHO" | 
         Senator == "VANESSA GRAZZIOTIN" | Senator == "JOSÉ MEDEIROS" | 
         Senator == "GLADSON CAMELI" | Senator == "HUMBERTO COSTA")
bp <- ggplot(dt,aes(Senator,Refunded)) + geom_boxplot()
vp <- ggplot(dt,aes(Senator,Refunded)) + geom_violin(scale="area")
  
#analysing Top 1 Spender (Paulo Rocha)

dt <- df %>%
  select(Month:dayWeek) %>%
  filter(Senator == "PAULO ROCHA")

dt1 <- dt %>%
  select(ExpenseType,Refunded) %>%
  group_by(ExpenseType) %>%
  summarise(Spend = round(sum(Refunded)/1000,2))%>%
  mutate(Legend=factor(c('1','2','3','4','5','6')))
a1 <- ggplot(dt1, aes(Legend,Spend)) + ggtitle("Expense Type of Paulo Rocha") + 
  xlab("ExpenseType") + geom_bar(stat="identity") + ylab("R$") + theme_minimal() + 
  legend("top",col=Legend,legend=ExpenseTypeName)
                    #Lembrar de explicar as legendas

dt1 <- dt %>%
  select(Month,Refunded) %>%
  group_by(Month) %>%
  summarise(Spend = round(sum(Refunded)/1000,2))
a2 <- ggplot(data = dt1, aes(x=Month,y=Spend, group=1)) + ggtitle("Evolution during the months") + 
  xlab("Months") + geom_point() + geom_line() + theme_minimal()

#g5: evolução dos gastos no dias da semana (Refunded-Month)
dt1 <- dt %>%
  select(dayWeek,Refunded) %>%
  group_by(dayWeek) %>%
  summarise(Spend = round(sum(Refunded)/1000,2)) %>%
  arrange(match(dayWeek,c("Monday","Tuesday","Wednesday",
                          "Thursday","Friday","Saturday","Sunday")))
a2 <- ggplot(dt1, aes(x=dayWeek,y=Spend, group=1)) + ggtitle("Evolution during the days") + 
  xlab("Days of the Week") + geom_point() + geom_line() + theme_minimal()





