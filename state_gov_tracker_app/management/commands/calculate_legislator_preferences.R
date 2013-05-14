# Calculate Ideal Points of Legislators
library("RPostgreSQL")
library("pscl")
library("ggplot2")

# Load Data 
# Path to SQLite Database #
conn <- dbConnect("PostgreSQL", dbname = "staterep")

print("Loading votes...")
# Get Votes Table
upper_chamber_vote_query <- dbSendQuery(conn, "select legid, vote, bill_id_id from legis_votes as l left join pa_legis_votes as p on(l.vote_id=p.vote_id_id) where chamber = 'upper' and type = 'passage'")
upper_votes = fetch(upper_chamber_vote_query, n=-1)

lower_chamber_vote_query <- dbSendQuery(conn, "select legid, vote, bill_id_id from legis_votes as l left join pa_legis_votes as p on(l.vote_id=p.vote_id_id) where chamber = 'lower' and type = 'passage'")
low_votes = fetch(lower_chamber_vote_query, n=-1)

# Get Member Table
mem_info <- dbReadTable(conn, "officials")
mem_data <- data.frame(cbind(mem_info$legid, mem_info$party, mem_info$chamber), stringsAsFactors = FALSE)

lower_mem <- subset(mem_data, X3 %in% c("lower"))
upper_mem <- subset(mem_data, X3 %in% c("upper"))

lower_legid <- lower_mem[1]
upper_legid <- upper_mem[1]

# Reshape Votes so that each row is a legislator and column is a vote
up_votes_wide <- reshape(upper_votes, idvar="legid", timevar="bill_id_id", direction="wide")
low_votes_wide <- reshape(low_votes, idvar="legid", timevar="bill_id_id", direction="wide")

print("Creating Roll Call Objects...")
# Create Roll Call Vote Object #
#colnames(votes_wide)[1] <- "legis.names"
len_up <- length(colnames(up_votes_wide))
len_low <- length(colnames(low_votes_wide))

# Separate out Upper and Lower Chambers #
upper_vote_wide_sub <- up_votes_wide[,2:len_up]
lower_vote_wide_sub <- low_votes_wide[,2:len_low]

# Create Roll Call Objects (drop legislators with less than 5 votes and drop votes with less than 5 in opposition)
rc_upper <- rollcall(upper_vote_wide_sub, missing=c(NA, 99), legis.names=up_votes_wide[,1])
rc_lower <- rollcall(lower_vote_wide_sub, missing=c(NA, 99), legis.names=low_votes_wide[,1])

rc_upper_fixed <- dropRollCall(rc_upper, dropList=list(lop=5))
rc_lower_fixed <- dropRollCall(rc_lower, dropList=list(lop=5))
up_sum <- summary(rc_upper_fixed)
low_sum <- summary(rc_lower_fixed)
# Calculate Ideal Points #

if (up_sum$m > 15) {
    print("Calculating ideal points for upper chamber...")
    id1 <- ideal(rc_upper_fixed,
                 d=1,
                 startvals="eigen",
                 normalize=TRUE,
                 store.item=TRUE,
                 maxiter=100000,
                 burnin=10000,
                 thin=100,
                 verbose=FALSE)
    
    # Combine Ideal Points with Party Data #
    ideal_scores_upper <- cbind(up_votes_wide[,1], id1$xbar)
    ideal_scores_upper <- data.frame(ideal_scores_upper, row.names=NULL)
    
    # Transform Variables into correct formats
    ideal_scores_upper$D1 <- as.numeric(levels(ideal_scores_upper$D1))[ideal_scores_upper$D1]
    combined_upper <- merge(upper_mem, ideal_scores_upper, by.x = "X1", by.y = "V1")
    combined_upper$X2 <- as.factor(combined_upper$X2)
    combined_upper$X3 <- as.factor(combined_upper$X3)
    
    for (i in 1:length(combined$D1)) {
        combined$D1[i] <- -1*combined$D1[i]
    }
    
    dbWriteTable(conn, "preferences", combined_upper, overwrite=TRUE)
} else {
    print("Not enough votes to calculate ideal points for upper chamber...")
}

if (low_sum$m > 15) {
    print("Calculating ideal points for lower chamber...")
    id2 <- ideal(rc_lower_fixed,
                 d=1,
                 startvals="eigen",
                 normalize=TRUE,
                 store.item=TRUE,
                 maxiter=100000,
                 burnin=10000,
                 thin=100,
                 verbose=FALSE)
    # Combine Ideal Points with Party Data #
    
    ideal_scores_lower <- cbind(low_votes_wide[,1], id2$xbar)
    ideal_scores_lower <- data.frame(ideal_scores_lower, row.names=NULL)
    
    # Transform Variables into correct formats
    
    ideal_scores_lower$D1 <- as.numeric(levels(ideal_scores_lower$D1))[ideal_scores_lower$D1]
    combined_lower <- merge(lower_mem, ideal_scores_lower, by.x = "X1", by.y = "V1")
    
    combined_lower$X2 <- as.factor(combined_lower$X2)
    combined_lower$X3 <- as.factor(combined_lower$X3)
    
    # If new upper chamber values are calculated, do not overwrite
    # lower chamber, just append. However, if no ideal points for upper 
    # chamber can be calculated, then do overwrite all values in preferences
    # table
    if (up_sum$m > 15) {
        combined <- rbind(combined_lower, combined_upper)
    } else {
        combined <- combined_lower
    }
} else {
    print("Not enough votes to calculate ideal points for lower chamber...")
}

print("Writing CSV file...")
write.table(combined, "./preferences.csv", sep=",", row.names=FALSE, col.names=FALSE)