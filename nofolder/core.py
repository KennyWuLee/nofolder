#
# core.py
#
# Copyright (C) 2009 KennyWuLee <krischer.till@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
import os
import re

DEFAULT_PREFS = {
    "dontaddfolder": False,
    "createfolder": False,
}

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("nofolder.conf", DEFAULT_PREFS)
        core = component.get("Core")
        self.torrent_manager = component.get("TorrentManager")
        self.torrents = core.torrentmanager.torrents
        component.get("EventManager").register_event_handler("TorrentAddedEvent", self.post_torrent_add)

    def disable(self):
        pass

    def update(self):
        pass

    def post_torrent_add(self, torrent_id):
        #if not self.torrent_manager.session_started or (not (self.config['dontaddfolder'] or self.config['createfolder'])):
        if not (self.config['dontaddfolder'] or self.config['createfolder']):
            return
        torrent = self.torrents[torrent_id]
        torrent.pause()
        status_keys = ["files", "save_path", "name"]
        status = torrent.get_status(status_keys)
        if self.config['dontaddfolder'] and re.match('.*/.*', status["files"][0]["path"]):
            namechanges = []
            for i in range(0, len(status["files"])):
                namechanges.append([i, status["files"][i]["path"].replace(status["name"] + "/", "")])
            torrent.rename_files(namechanges)
            torrent.force_recheck()
        if self.config['createfolder'] and not re.match('.*/.*', status["files"][0]["path"]):
            torrent.rename_files([[0, os.path.splitext(status["name"])[0] + "/" + status["files"][0]["path"]]])
            torrent.force_recheck()
        torrent.resume()

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
