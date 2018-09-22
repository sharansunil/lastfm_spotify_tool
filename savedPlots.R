library(ggplot2)
library(dplyr)
library(fmsb)
library(tidyverse)
library(svglite)
library(gdtools)

rm(list=ls())
par(mfrow=c(2,2),mar=c(4,1,4,1), oma=c(1,0,1,0))

setwd("~/Documents/spotify-hacks")

df<-read.csv("exports/artistProfile.csv",row.names=1)


