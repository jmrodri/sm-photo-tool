/*
 * create.go
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

// createCmd represents the create command
var createCmd = &cobra.Command{
	Use:   "create",
	Short: "create a new gallery and uploads the given files.",
	Long: `create a new gallery and uploads the given files to it, ignoring
	any previous upload state. Use the --upload option if you want to do a
	one-time upload to a new gallery without messing up future updates.`,
	Run: func(cmd *cobra.Command, args []string) {
		// TODO: Work your own magic here
		fmt.Println("Running create command")
	},
}

func init() {
	RootCmd.AddCommand(createCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// createCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// createCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
	createCmd.Flags().StringP("category", "", "", "Parent category for album")
	createCmd.Flags().StringP("subcategory", "", "", "Parent category for album")
	createCmd.Flags().StringP("description", "", "", "Gallery description")
	createCmd.Flags().StringP("keywords", "", "", "Gallery description")
	createCmd.Flags().StringP("gallery_password", "", "", "Gallery password")
	createCmd.Flags().BoolP("private", "", false, "make gallery private, [default: public]")
	createCmd.Flags().BoolP("showfilenames", "", true, "show filenames in the gallery, [default: true]")
	createCmd.Flags().BoolP("squarethumbs", "", false, "square thumbs in the gallery,, [default: false]")
	createCmd.Flags().BoolP("hideowner", "", false, "hide ownership, [default: false]")
	createCmd.Flags().StringP("sortmethod", "", "", "define sort method, [default: Position]")
	createCmd.Flags().BoolP("no-comments", "", false, "disallow comments")
	createCmd.Flags().BoolP("no-external-links", "", false, "disallow external links")
	createCmd.Flags().BoolP("no-camera-info", "", false, "do not show camera info")
	createCmd.Flags().BoolP("no-easy-sharing", "", false, "disable easy sharing")
	createCmd.Flags().BoolP("no-print-ordering", "", false, "disable print ordering")
	createCmd.Flags().BoolP("no-originals", "", false, "disable originals")
	createCmd.Flags().BoolP("no-world-searchable", "", false, "disable world searchability")
	createCmd.Flags().BoolP("no-smug-searchable", "", false, "disable smug searchability")
	createCmd.Flags().StringP("community", "", "", "specifies the gallery's community")
	filter_regex_default := ".*\\.(jpg|gif|avi|m4v|mp4|JPG|GIF|AVI|M4V|MP4)"
	//createCmd.Flags().StringP("filter-regex", "", filter_regex_default,
	//		"Only upload files that match. [default: %s]", filter_regex_default)
	createCmd.Flags().StringP("filter-regex", "", filter_regex_default, "Only upload files that match. [default: %s]")
	createCmd.Flags().BoolP("upload", "", false, "upload images, ignoring previous upload state")
	createCmd.Flags().IntP("max_size", "", 800000000, "Maximum file size (bytes) to upload. [default: 800000000]")
}
