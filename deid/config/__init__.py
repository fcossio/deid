"""

DeidRecipe

Copyright (c) 2017-2022 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The functions below assume a configuration file called deid, although the
user can specify a custom name.


"""

from deid.config.utils import load_deid, get_deid, load_combined_deid
from deid.config.standards import actions, sections, formats

from deid.logger import bot


class DeidRecipe:
    """Create a deid recipe to filter and perform operations on a dicom header.

    Usage typically looks like:

    deid = 'dicom.deid'
    recipe = DeidRecipe(deid)

    If deid is None, the default provided by the application is used.

    Parameters
    ==========
    deid: the deid recipe (or recipes) files to use. If more than one
          is provided, should be done in order of preference for load
          (later in the list overrides earlier loaded).
    base: if True, load a default base (default_base) before custom
    default_base: the default base to load if "base" is True

    """

    def __init__(self, deid=None, base=False, default_base="dicom"):

        # If deid is None, use the default
        if deid is None:
            base = True

        self._init_deid(deid, base=base, default_base=default_base)

    def __str__(self):
        return "[deid]"

    def __repr__(self):
        return "[deid]"

    def load(self, deid):
        """
        Load a deid recipe into the object.

        If a deid configuration is already defined, append to that.
        """
        deid = get_deid(deid)
        if deid is not None:

            # Update our list of files
            self._files.append(deid)
            self.files = list(set(self.files))

            # Priority here goes to additional deid
            self.deid = load_combined_deid([self.deid, deid])

    def _get_section(self, name):
        """
        Return a section (key) in the loaded deid, if it exists
        """
        section = None
        if self.deid is not None:
            section = self.deid.get(name)
        return section

    # Get Sections

    def get_format(self):
        """
        Return the format of the loaded deid, if one exists
        """
        return self._get_section("format")

    def _get_named_section(self, section_name, name=None):
        """Get a named section from the deid recipe.

        a helper function to return an entire section, or if a name is
        provided, a named section under it. If the section is not
        defined, we appropriately return None.
        """
        section = self._get_section(section_name)
        if name is not None and section is not None:
            section = section.get(name, [])
        return section

    def get_filters(self, name=None):
        """
        Return all filters for a deid recipe, or a set based on a name
        """
        return self._get_named_section("filter", name)

    def get_values_lists(self, name=None):
        """
        Return a values list by name
        """
        return self._get_named_section("values", name)

    def get_fields_lists(self, name=None):
        """
        Return a values list by name
        """
        return self._get_named_section("fields", name)

    def _get_actions(self, action=None, field=None, section="header"):
        """
        Handler for header or filemeta actions.
        """
        header = self._get_section(section) or []
        if header is not None:
            if action is not None:
                action = action.upper()
                header = [x for x in header if x["action"].upper() == action]
            if field is not None:
                field = field.upper()
                header = [x for x in header if x["field"].upper() == field]
        return header

    def get_actions(self, action=None, field=None):
        """Get deid actions to perform on a header, or a subset based on a type

        A header action is a list with the following:
        {'action': 'REMOVE', 'field': 'AssignedLocation'},

        Parameters
        ==========
        action: if not None, filter to action specified
        field: if not None, filter to field specified

        """
        return self._get_actions(action, field)

    # Boolean properties

    def _has_list_content(self, name):
        return len(self.deid.get(name, [])) > 0

    def has_fields_lists(self):
        return self._has_list_content("fields")

    def has_values_lists(self):
        return self._has_list_content("values")

    def has_actions(self):
        return self._has_list_content("header")

    # Listing

    def listof(self, section):
        """
        Return a list of keys for a section
        """
        listing = self._get_section(section) or {}
        return list(listing.keys())

    def ls_filters(self):
        return self.listof("filter")

    def ls_valuelists(self):
        return self.listof("values")

    def ls_fieldlists(self):
        return self.listof("fields")

    # Init

    def _init_deid(self, deid=None, base=False, default_base="dicom"):
        """Initialize a recipe.

        initialize the recipe with one or more deids, optionally including
        the default. This function is called at init time. If you need to add
        or work with already loaded configurations, use add/remove

        Parameters
        ==========
        deid: the deid recipe (or recipes) files to use. If more than one
              is provided, should be done in order of preference for load
              (later in the list overrides earlier loaded).
        default_base: load the default base before the user customizations.

        """
        if deid is None:
            deid = []

        if not isinstance(deid, list):
            deid = [deid]

        if base is True:
            deid.append(default_base)

        self._files = deid

        if len(deid) == 0:
            bot.info("You can add custom deid files with .load().")
        self.deid = load_combined_deid(deid)
