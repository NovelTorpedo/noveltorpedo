# Future improvements

These are features we would like to have eventually, but cannot be added to the MVP due to time constraints.

## 1 Account features

These features will be available for the two types of account currently implemented in NovelTorpedo.

### 1.1 User Accounts

These features will be available for users who have an account registered with the website.

#### 1.1.1 Reading History

Users will be able to view and clear their reading history.

This could be implemented by appending the URL of each link a user clicks on with a timestamp to a table of entries for each user, and then making this table displayable via a web page.

Then, give the user a button on this web page that deletes all entries affiliated with their user ID.

#### 1.1.2 Favorites

Users will be able to add, remove, and view stories to a &quot;favorites&quot; list associated with their registered account.

This could be implemented in a similar way to how Reading History (see section 1.1) is implemented with two main distinctions.

Rather than automatically added the url to the &quot;favorites&quot; list, NovelTorpedo could provide the user with a &quot;favorite&quot; button available after clicking on a story.

Additionally, &quot;favorited&quot; items should removable by the user individually. This could be implemented by providing a &quot;remove&quot; button next to each story in the list of &quot;favorites&quot;.

#### 1.1.3 Detailed Tagging

Users can create tags for literature they have read, in addition to the NSFW tagging already included in the MVP. These tags will need to be separate from the tags gathered by the web scrapers, since users will be able to remove tags they have created.

Some possible tags include:

- Completion status
- Universe
- Funny

This could be implemented by having incrementing values in StoryAttributes; for example, if a piece is marked as &quot;Funny&quot;, a StoryAttributes entry could be created with **Key**&quot;TagFunny&quot; and its **Value** initially set to 1.

Tags will be displayed on a popularity basis. To prevent inappropriate tagging or trolling, common tags should be highly visible, and unique tags less visible. For example, displaying only the five most common user-made tags for each **Story** should edge out less common &quot;troll&quot; tags.

These features will be available for administrators of the website.

#### 1.2.1 Remove Story from Search Results

Administrators can prevent a story from being displayed to users.

This can be implemented by adding to the current DB schema (see section 4.6 Viewable Stories) and expanding on Django&#39;s administrator capabilities.

## 2 Database API

An API will be created to interface with the database.

## 3 Features for Authors

The following features are for authors of stories tracked by NovelTorpedo.

### 3.1 Author Differentiation

A method of differentiating authors beyond their name may be developed so that authors with identical names can have their individual profiles tracked. This works in part towards enabling subsection 3.2.

### 3.2 Patreon Accounts

Links will be available to patreon accounts or similar popular purchase sites of authors. This feature is somewhat reliant on the above.

API for database released to public.

Links to patreon accounts.

## 4 Story features

In this section, we describe features that could be added to the architecture of NovelTorpedo  to better differentiate Stories and identify them.

### 4.1 Duplicate detection

Multiple copies of a work that differ slightly might be unintentionally added to the database as separate works; this is potentially unsolvable, since creators can edit their own work in one location, and forget to update listings on separate sites.

A suggested first step to addressing this issue would be to use ElasticSearch&#39;s [MoreLikeThis](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-mlt-query.html) feature to remove exceptionally similar stories. One danger to this approach is that this would likely remove the common form of parody works where an Author takes another Author&#39;s Story and then changes names and verbs to change the context, which is a perfectly valid form of web fiction.

### 4.2 Sequel information

NovelTorpedo will store sequel relationships between pieces of literature.

### 4.3 Updated Posts

NovelTorpedo will notice when a new post is added to a story. NovelTorpedo&#39;s implementation, as is, will **not** look at a **Story** if it was last posted to before it had last been scraped; however, the case may arise where a Story&#39;s post is edited (or a hidden post revealed), but a new post is not added, so the timestamp of the Story does not change. Similarly, NovelTorpedo will not notice if a post is removed.

One of the simplest methods to amend this would be to periodically wipe the database and start anew; it seems out of scope for this product to be used to link to a Story that no longer exists.

### 4.4 Internet Archive Reference

NovelTorpedo will have a reference to a story&#39;s internet archive snapshot. With our current DB schema, this should a variable of the StoryHost class.

To populate this field, NovelTorpedo could use one of The Internet Archive&#39;s [&quot;Wayback Machine&quot; APIs](https://archive.org/help/wayback_api.php) for querying the url of an archived snapshot for a given site.

Currently, there isn&#39;t a way of requesting a site be archived through Internet Archive&#39;s APIs, only manually. So the archive snapshot may not exactly match the contents of the corresponding story (if the last time the scraper updated the story contents was more recent than the last snapshot made by Internet Archive). Developers of NovelTorpedo may want to add a disclaimer conveying that information to users or find another way of submitting a site to be archived by The Internet Archive when stories are scraped.

### 4.5 Deleted Stories

NovelTorpedo will notice when a story is removed from the host on which we&#39;re tracking it. This feature is only useful if the previous feature (Internet Archive Reference, section 4.4) is implemented. As with the internet archive reference, this should be a variable of the StoryHost class.

This tag should be used as an indication to the corresponding scraper of the story&#39;s source that it should not try to continue collecting updates on the removed story.

Additionally, the source provided to the user of a given deleted story will be replaced by its most recent internet archive reference rather than its original host website.

### 4.6 Viewable Stories

NovelTorpedo will have a visibility tag that will automatically be set to True. If a user requests that the content of their story be removed from the site, administrators can set this variable to False, preventing a given story from being displayed in search results.

As oppose to just removing the contents of a given story from the database entirely, this prevents the situation where an author requests their story be removed, the story is removed, and another user again submits the story, making it again available for searches.

This should be implemented as a variable in the Story class in models.py that is checked in the StoryIndex class of search\_indexes.py.

## 5 Website features

In this section, we describe features that could potentially be added to the website, as well as methods of implementing them.

### 5.1 Adding New Content Form will Keep Info about Future Sites to Scrape

If the Add Story page is someday extended to add more stories than just Tumblr blogs, the case may arise where a user enters a website not currently being scraped by NovelTorpedo. In the case where the site suggested by the user is not one that we are currently scraping, it should get added to a list of suggested future sites to scrape.

This could be appended to a database table made for this purpose, such as SuggestedStoryHosts. The scraper for this website would, of course, have to be implemented manually.

### 5.2 Filtering Searches

This section covers more thorough search options for users.

Implementing any of these features will require modifications to NovelTorpedo&#39;s SearchForm class (found in forms.py). For more details, see [Creating Your Own Form](http://django-haystack.readthedocs.io/en/v2.6.0/views_and_forms.html) and the filter function in Haystack&#39;s documentation.

#### 5.2.1 Exploring Stories by Author

It may be desired to search for stories by author instead of by the contents of the story. As-is, NovelTorpedo&#39;s Search functionality searches both the Authors and the contents of the Story based on what&#39;s put into the query bar on the main web page.

A radio button to search specifically by Story content or by the Authors of stories could be implemented beside the search bar.

Filtering the searches exclusively by author can be done using haystack&#39;s filter method.

#### 5.2.2 Exploring Stories by Tag

Similarly to the previous section, users may desire to search for stories containing a particular tag. Currently, NovelTorpedo does not search by story tags.

Story tags should be included in general searches. To implement this, a Hackstack search will have to be created to search through StoryAttribute objects, as opposed to just searching through Story objects as it does now (see NovelTorpedo&#39;s models.py, search\_indexes.py, and story\_text.py).

Additionally, as with Exploring Stories by Author, a radio button next to the search bar to search by Tag should be implemented for exclusive tag searches.

#### 5.2.3 Filter Search by Maturity

Users may want to exclude stories marked as mature from their searches.

This can be done one of two ways:

By searching through StoryAttributes, checking for tags listed as &quot;mature&quot;, and excluding corresponding stories from the results. This option relies on users, either from a story&#39;s host or those registered in NovelTorpedo, tagging stories as mature.

Alternatively and ideally, when a story is added to or updated in NovelTorpedo&#39;s DB, the flags and words in the contents of the story (see StoryAttribute and StorySegment.content in models.py) would be checked for matches with those found within a list of &quot;mature content&quot; words. If any are found, a &quot;mature&quot; variable in the Story class (see models.py) would be set. This variable can then be used as a filter for searches. This process of checking for mature content should be not be a responsibility of the scrapers, but a separate process that periodically runs through all StoryHosts in the DB, checking the &quot;last\_scraped&quot; date variable, and if that date is more recent than the last time the process ran, then goes through and checks the corresponding story&#39;s StoryAttributes and StorySegment contents. This option would be far more work for developers and for NovelTorpedo, but more thorough.

Either way, a checkbox to include or exclude mature content in searches could be added next to the search bar, indicating to NovelTorpedo&#39;s SearchForm whether to filter out mature content.

### 5.3 Contact/Disclaimer Page

This page provides users with NovelTorpedo&#39;s use policy and a means of contact.

It should notify users that the snippets of stories provided by NovelTorpedo falls under fair use according to the ruling of Authors Guild, Inc. v. Google, Inc., even for published stories, as well as provide users with a means of contacting the site administrators if they have any questions or concerns.

[HelloWebApp](https://hellowebapp.com/news/tutorial-setting-up-a-contact-form-with-django/) provides a straightforward tutorial on how to do this. To add a link to the page in the header of all pages, modify templates/noveltorpedo/partials/header.html.

## 6 Adding Scrapers

The developers in charge of NovelTorpedo may want to add additional scrapers to scrape different websites. If you are using scrapy, create another scrapy project in the &quot;noveltorpedo/scrapers&quot; directory.

Create a spider that will traverse your website, and add code to actually run the spider in the &quot;spider\_manager.py&quot; script. You will call this script once, and the spider will continually crawl the website and restart when it is finished.
