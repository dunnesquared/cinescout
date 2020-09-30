# Cinescout – Live Site

## Important information regarding v1.1.0 
### Septemeber 30, 2020
Out of a desire to make the live version of `Cinescout` available to everyone as fast as possible, 
I have taken away and added some features. Most notably, I have removed the ability for users to 
create their own accounts. The security behind the feature was rather primitive, and would 
require a lot more work to feel confident that I'm doing an adequate job protecting users' data. 
Moreover, it was never my intention to scale the project and maintain a large database. But who
knows—maybe I'll change my mind some day.

I've also hidden NYT movie reviews from anonymous users. I wish I could display them, but the NYT 
api has a key limit of 4000 requests per day, 10 requests per minute. Although it's highly unlikely 
that  `Cinescout` would ever achieve that level of traffic, I just don't like users not being able
to use the site because of 429 errors.

That said, registered users can still see NYT reviews and create personal lists, who I'm 
limiting now to family, friends and potential employers interested in seeing all the features of the 
app. To administering the site easier, I've implemented a rather basic admin panel using 
Flask-admin to add users and reset passwords willy-nilly.