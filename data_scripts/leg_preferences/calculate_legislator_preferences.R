# Calculate Ideal Points of Legislators
library("RSQLite")
library("pscl")
library("ggplot2")

# Load Data 
# Path to SQLite Database #
conn <- dbConnect("SQLite", dbname = "/home/christopher/Dropbox/CongressMonitor/StateGovTracker.db")

# Get Votes Table
votes <- dbReadTable(conn, "pa_legis_votes")
vote_sub <- votes[,1:3]

# Get Member Table
mem_info <- dbReadTable(conn, "officials")
mem_data <- data.frame(cbind(mem_info$legid, mem_info$party, mem_info$chamber))

# Reshape Votes so that each row is a legislator and column is a vote
votes_wide <- reshape(vote_sub, idvar="legid", timevar="bill_id", direction="wide")

# Create Roll Call Vote Object #
colnames(votes_wide)[1] <- "legis.names"
length(colnames(votes_wide))
vote_wide_sub <- votes_wide[,2:699]
rc <- rollcall(vote_wide_sub, legis.names=votes_wide[,1])

# Calculate Ideal Points #
id1 <- ideal(rc,
             d=1,
             startvals="eigen",
             normalize=TRUE,
             store.item=TRUE,
             maxiter=10000,
             burnin=1000,
             thin=100,
             verbose=TRUE)  

# Combine Ideal Points with Party Data #
ideal_scores <- cbind(votes_wide[,1], id1$xbar)
ideal_scores <- data.frame(ideal_scores, row.names=NULL)

# Transform Variables into correct formats
ideal_scores$D1 <- as.numeric(levels(ideal_scores$D1))[ideal_scores$D1]
combined <- merge(mem_data, ideal_scores, by.x = "X1", by.y = "V1")
combined$X2 <- as.factor(combined$X2)
combined$X3 <- as.factor(combined$X3)

for (i in 1:length(combined$D1)) {
    combined$D1[i] <- -1*combined$D1[i]
}

# Generate Kernel Density Plots #
dist <- ggplot(combined, aes(x=D1)) + geom_density(alpha=.2, fill="#FF6666") 
dist + facet_grid(X2 ~ X3)
