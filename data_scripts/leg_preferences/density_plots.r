# Calculate Ideal Points of Legislators
library("RSQLite")
library("pscl")
library("ggplot2")
library(sm)

# Load Data 
# Path to SQLite Database #
conn <- dbConnect("SQLite", dbname = "/home/christopher/Dropbox/CongressMonitor/StateGovTracker.db")

# Get Votes Table
votes <- dbReadTable(conn, "preferences")
votes$ideology <- as.numeric(votes$ideology)

d <- density(votes$ideology)
plot(d)

attributes(d)
density_r_upper <- density(votes[votes$party=="Republican" & votes$chamber == "upper",]$ideology)
density_d_upper <- density(votes[votes$party=="Democratic" & votes$chamber == "upper",]$ideology)
density_r_lower <- density(votes[votes$party=="Republican" & votes$chamber == "lower",]$ideology)
density_d_lower <- density(votes[votes$party=="Democratic" & votes$chamber == "lower",]$ideology)
plot(density_r_upper)

## Combine Data ##
r_upper <- cbind(density_r_upper$x, density_r_upper$y, c('Republican'), c('upper'))
d_upper <- cbind(density_d_upper$x, density_d_upper$y, c('Democratic'), c('upper'))
r_lower <- cbind(density_r_lower$x, density_r_lower$y, c('Republican'), c('lower'))
d_lower <- cbind(density_d_lower$x, density_d_lower$y, c('Democratic'), c('lower'))

combined_kdensity <- data.frame(rbind(r_upper, r_lower, d_upper, d_lower))

dbWriteTable(conn, "preferences_kdensity", combined_kdensity, overwrite=TRUE)