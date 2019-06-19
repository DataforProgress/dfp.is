library(crunch)
library(stringi)

save_question_csv <- function(ds){
  qs <- data.frame(variables(ds))
  qs <- data.frame(alias=qs$alias, name=qs$name, type=qs$type,  description=descriptions(variables(ds)))
  
  cats <- function(id){
    id <- as.character(id)
    catsx <- categories(ds[[id]])
    cats_str = ""
    if (is.Categorical(ds[[id]])){
      for(catx in catsx){
        if (!catx$missing){
          cats_str<-paste(cats_str, stri_trim_both(catx$name), sep=";")
        }
      }
    }
    return(cats_str)
  }
  
  qs$categories <- sapply(qs$alias, cats)
  qs$survey_name <- name(ds)
  qs$survey_code <- stri_replace_all_fixed(name(ds), " ", "")
  return(qs)
}

urls <- list("https://app.crunch.io/dataset/2edf36e084ba4e088e5a3efdcf37714f/",
             "https://app.crunch.io/dataset/ccf8ab5d1bf14c9ebd7946877e53cf5f/")

qs <- data.frame()

for (url in urls){
  qs <- rbind(qs, save_question_csv(loadDataset(url)))
}

write.csv(qs, paste("qs_full", ".csv", sep=""))

