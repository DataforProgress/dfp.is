library(crunch)
library(stringi)

save_question_csv <- function(ds){
  ts <- data.frame(variables(ds))
  qs <- data.frame(alias=ts$alias, name=ts$name, type=ts$type,  description=descriptions(variables(ds)))
  
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
    cats_str <- substring(cats_str, 2)
    return(cats_str)
  }
  
  print(cats)
  
  qs$categories <- sapply(qs$alias, cats)
  qs$survey <- stri_replace_all_fixed(name(ds), " ", "")
  qs$survey_name <- name(ds)
  #write.csv(ds, paste(qs$survey, ".csv"))
  return(qs)
}


# use one of these to iterate over dataset names/urls that can be loaded from

dss <- datasets()
qs <- save_question_csv(loadDataset(dss[[1]]@entity_url))
for (i in seq(2, length(dss))){
  url <- dss[[i]]@entity_url
  q <- save_question_csv(loadDataset(url))
  print(colnames(q))
  qs <- rbind(qs, q)
}

write.csv(qs, paste("qs_full", ".csv", sep=""))

