#package
library(dplyr)
library(plyr)
library(randomForest)
library(lattice)
library(ggplot2)
library(caret)
library(gmodels)
library(e1071)


#load and visualization data
df_teste <- read.csv("dataset/train_sample.csv",sep = ",",header = T)
View(df_teste)
str(df_teste)
glimpse(df_teste)


#DATA MUNGING--------------------------------------------------------------------------------------------------------

#drop na data
df_teste <- na.omit(df_teste)

#transform is_attributed into type factor
df_teste$is_attributed <- as.factor(df_teste$is_attributed)

#calculating how long in seconds it took to download
attributed = df_teste[df_teste$is_attributed == '1','attributed_time']
click = df_teste[df_teste$is_attributed == '1','click_time']
dif <- as.double(difftime(attributed,click))

#placing No in the assigned_time col where it was not downloaded and placing it in the char type
df_teste$attributed_time <- as.character(mapvalues(df_teste$attributed_time, from=c(""), to=c('No')))

# putting the time spent and already dividing the time into 7 levels ("No", "-1", "1-5", "5-10", "10-30", "30-60", "60+ ") in minute
diff = 1
for (i in 1:length(df_teste$ip)){
  if (df_teste[i,'is_attributed'] == '1'){
    if (dif[diff] < 60){
      df_teste[i,'attributed_time'] = '-1'
    }else if (dif[diff] >= 60 & dif[diff] < 300){
      df_teste[i,'attributed_time'] = '1-5'
    }else if (dif[diff] >= 300 & dif[diff] < 600){
      df_teste[i,'attributed_time'] = '5-10'
    }else if (dif[diff] >= 600 & dif[diff] < 1800){
      df_teste[i,'attributed_time'] = '10-30'
    }else if (dif[diff] >= 1800 & dif[diff] < 3600){
      df_teste[i,'attributed_time'] = '30-60'
    }else if (dif[diff] >= 3600){
      df_teste[i,'attributed_time'] = '60+'
    }
    diff = diff+1
  }
}

#return attribute_time to factor
df_teste$attributed_time <- as.factor(df_teste$attributed_time)

#mapping the is_attributed values to Yes and No
df_teste$is_attributed <- mapvalues(df_teste$is_attributed, from=c("0","1"), to=c("No","Yes"))

#exclude the click_time column, as your information is already in attributed_time
df_teste$click_time <- NULL

#FEATURE SELECTION---------------------------------------------------------------------------------------------------

#evaluate the features using the random forest

#first, using all features
modelo1 <- randomForest(is_attributed ~ ., 
                       data = df_teste, 
                       ntree = 100, 
                       nodesize = 10,
                       importance = TRUE)
varImpPlot(modelo1)

#second: not using attributed_time
modelo2 <- randomForest(is_attributed ~ .-attributed_time , 
                       data = df_teste, 
                       ntree = 100, 
                       nodesize = 10,
                       importance = TRUE)
varImpPlot(modelo2)

#by the result of the two models, we will exclude the feature: device
df_teste$device <- NULL


#MACHINE LEARNING----------------------------------------------------------------------------------------------------

#split the data
index <- createDataPartition(df_teste$is_attributed, p=0.7, list=F)
training <- df_teste[index,]
validating <- df_teste[-index,]

#MODEL 1: SVM
mod1 <- svm(is_attributed ~ ., data=training, type='C-classification', kernel='radial')
pred1 <- predict(mod1,validating)
tab1 = table(Predicted=pred1, Actual=validating$is_attributed)
summary(mod1)
accuracy <- function(x){sum(diag(x)/(sum(rowSums(x)))) * 100}
accuracy(tab3)

#MODEL 2: Random Florest
mod2 <- randomForest(is_attributed ~ ., data=training)
pred2 <- predict(mod2,validating)
tab2 = table(Predicted=pred2, Actual=validating$is_attributed)
summary(mod2)
accuracy <- function(x){sum(diag(x)/(sum(rowSums(x)))) * 100}
accuracy(tab2)


















