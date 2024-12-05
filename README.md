# General Planning

## URLs

I've thought of the following URLs, as well as where they'll lead.
Of course, feel free to modify this list as needed.

* `/`
  * Welcome page
  * Doesn't require login
* `/users/`
  * Redirects to `/users/login/` if the user is not logged in
  * Redirects to `/users/{id}/` if the user is already logged in
* `/users/login/`
  * Redirects to `/users/{id}/` if the user is logged in
  * Uses React scripts to prevent form submission without all fields filled
    * Script will submit a `POST` to the same address to submit the login request
* `/users/new/`
  * Redirects to `/` if the user is logged in
  * Uses React scripts to prevent form submission without all fields filled
    * Script will submit a `POST` to the same address to submit the login request
  * Perhaps this and `/log-in/` could be a single page, with a clientside router between the two
    forms
* `/users/{id}/`
  * Sends 403 if the user is the wrong user
  * Displays user's info, allowing them to Delete the user entirely
* `/users/logout/`
  * Logs out the current user, if any, and redirects to `/`
* `/campaigns/`
  * Redirects to `/` if the user is not logged in
  * Displays all of the current user's campaigns
    * Including the campaign description
    * Perhaps a summary of how many locations, characters, etc. have been added to the campaign
    * Whether the campaign is public or private
* `/campaigns/{id}/`
  * Redirects to `/` if the user is not logged in
  * Sends 401 if the user is the wrong user
  * Displays the campaign details
    * Including the campaign description
    * Includes links to all related resources (locations, characters, etc.)
* `/campaigns/{id}/list/`
  * where `list` is one of `notes`, `locations`, `organizations`, `characters`, or `events`
  * Displays all Notes, Locations, etc. belonging to that campaign, with links to details for each
* `/campaigns/{id}/list/{id}/`
  * where `list` is one of `notes`, `locations`, `organizations`, `characters`, or `events`
  * Displays the given Note, Location, etc., along with an `Edit` and `Delete` button
  * All related locations, characters, etc. to the given item are linked

## Models

These are what I've got thus far. The list can be expanded, of course, but this seems like a good
starting point.

* `User`
  * Self-evident
  * Saves first name, last name, username (unique), email (unique), and password hash
* `Campaign`
  * Saves the DM (`User`), a name, description, and all approved users
    * Approved users cannot modify any fields, but they can view them
    * The campaign can also be set to `public`, negating the approved users field
* `Location`
  * Must belong to a campaign
    * I could change this if needed - for example, if the same land is used in multiple campaigns
  * Knows its name, description, and neighboring locations
  * Can be set to a Hostility setting (Friendly, Neutral, or Hostile. It'll be a dropdown)
* `Organization`
  * Belongs to a campaign and may belong to a location
  * Bears related organizations (e.g., a military group that's related to a governing body) and a
    Hostility setting
* `Character`
  * Belongs to a campaign and may belong to a location
  * Has a Race, which is Human by default, but can be any text field
  * Has a Class, which must be one of the 11 stock classes or Artificer
    (It can be a dropdown for simplicity)
  * Can belong to one or many organizations
  * `PlayerCharacter`
    * An extension of `Character`, adding a Player (`User`) field
  * `NonPlayerCharacter`
    * An extension of `Character`, adding a Hostility field
* `Event`
  * Basically holds any or all of the other fields, as well as a Time field (perhaps we should
    create an internal calendar similar to Star Wars' BBY and ABY, where we just time everything
    based on the campaign - BSC or ASC for Before Start of Campaign and After)
  * Can also hold a Duration field, default 0
* `Note`
  * This is a general Note that can effectively hold any desired information, used mainly for if
    someone needs to write a very quick note and convert it to another field later
  * Perhaps we could incorporate a `Convert To...` button to transition seamlessly from a Note to
    a Location, Event, Character, etc.
