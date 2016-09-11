/*
 * full_update.go
 *
 * Copyright (C) 2016 Jesus M. Rodriguez
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// full_updateCmd represents the full_update command
var full_updateCmd = &cobra.Command{
	Use:   "full_update",
	Short: "Mirror an entire directory tree.",
	Long: `The current working directory and all its subdirectories are
	examined for suitable image files.  Directories already corresponding to
	galleries, an update is performed. Directories not already known to be
	created on smugmug, are created there and all the appropriate image files
	are uploaded. The new gallery is named with the corresponding directory's
	relative path to the working directory where the command was invoked.
	This can be overridden with a file named Title in the relevant directory.
	If this exists, its contents are used to name the new gallery.`,
	Run: func(cmd *cobra.Command, args []string) {
		// TODO: Work your own magic here
		fmt.Println("full update command called")
	},
}

func init() {
	RootCmd.AddCommand(full_updateCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// full_updateCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// full_updateCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
	full_updateCmd.Flags().StringP("category", "", "", "Parent category for album")
	full_updateCmd.Flags().StringP("subcategory", "", "", "Parent category for album")
	full_updateCmd.Flags().StringP("description", "", "", "Gallery description")
	full_updateCmd.Flags().StringP("keywords", "", "", "Gallery description")
	full_updateCmd.Flags().StringP("gallery_password", "", "", "Gallery password")
	full_updateCmd.Flags().BoolP("private", "", false, "make gallery private, [default: public]")
	full_updateCmd.Flags().BoolP("showfilenames", "", true, "show filenames in the gallery, [default: true]")
	full_updateCmd.Flags().BoolP("squarethumbs", "", false, "square thumbs in the gallery,, [default: false]")
	full_updateCmd.Flags().BoolP("hideowner", "", false, "hide ownership, [default: false]")
	full_updateCmd.Flags().StringP("sortmethod", "", "Position", "define sort method, [default: Position]")
	full_updateCmd.Flags().BoolP("no-comments", "", false, "disallow comments")
	full_updateCmd.Flags().BoolP("no-external-links", "", false, "disallow external links")
	full_updateCmd.Flags().BoolP("no-camera-info", "", false, "do not show camera info")
	full_updateCmd.Flags().BoolP("no-easy-sharing", "", false, "disable easy sharing")
	full_updateCmd.Flags().BoolP("no-print-ordering", "", false, "disable print ordering")
	full_updateCmd.Flags().BoolP("no-originals", "", false, "disable originals")
	full_updateCmd.Flags().BoolP("no-world-searchable", "", false, "disable world searchability")
	full_updateCmd.Flags().BoolP("no-smug-searchable", "", false, "disable smug searchability")
	full_updateCmd.Flags().StringP("community", "", "", "specifies the gallery's community")
	filter_regex_default := ".*\\.(jpg|gif|avi|m4v|mp4|JPG|GIF|AVI|M4V|MP4)"
	full_updateCmd.Flags().StringP("filter-regex", "", filter_regex_default,
		"Only upload files that match. [default: %s]")
	full_updateCmd.Flags().BoolP("upload", "", false, "upload images, ignoring previous upload state")

}
