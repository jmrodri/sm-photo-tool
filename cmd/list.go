/*
 * list.go
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

// listCmd represents the list command
var listCmd = &cobra.Command{
	Use:   "list",
	Short: "Lists the files in an album, or lists available galleries",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		// TODO: Work your own magic here
		fmt.Println("list called")
	},
}

// albumCmd represents the list command
var albumCmd = &cobra.Command{
	Use:   "album",
	Short: "Lists the files in an album",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		var oid string
		if len(args) > 0 {
			oid = args[0]
		}
		fmt.Println("list_files(" + oid + ")")
	},
}

// galleriesCmd represents the list command
var galleriesCmd = &cobra.Command{
	Use:   "galleries",
	Short: "Lists the files in an galleries",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("list_galleries")
	},
}

func init() {
	RootCmd.AddCommand(listCmd)
	listCmd.AddCommand(albumCmd)
	listCmd.AddCommand(galleriesCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// listCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// listCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")

}
