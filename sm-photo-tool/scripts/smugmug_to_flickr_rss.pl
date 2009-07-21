#!/usr/bin/perl
use strict;
use LWP;
use XML::RSS;

my $req = HTTP::Request->new(GET => 'http://familiarodriguez.smugmug.com/hack/feed.mg?Type=nicknameRecentPhotos&Data=familiarodriguez&format=rss200');
my $ua = LWP::UserAgent->new;
my $resp = $ua->request($req);

# rss feed
# my $resp->content;
my $smugrss = new XML::RSS;
$smugrss->parse($resp->content);

my $s2frss = new XML::RSS;
$s2frss->add_module(prefix=>'media', uri=>'http://search.yahoo.com/mrss/');

# copy the channel
my $smugchan = $smugrss->{'channel'};
$s2frss->channel(title  => $smugchan->{'title'},
                 link   => $smugchan->{'link'},
                 description => $smugchan->{'description'},
                 pubDate => $smugchan->{'pubDate'},
                 lastBuildDate => $smugchan->{'lastBuildDate'},
                 generator => $smugchan->{'generator'},
                 copyright => $smugchan->{'copyright'});

$s2frss->image(title => $smugrss->{'image'}->{'title'},
               url   => $smugrss->{'image'}->{'url'},
               link  => $smugrss->{'image'}->{'link'});

# copy items
foreach my $item (@{$smugrss->{'items'}}) {
   $s2frss->add_item(
      title       => $item->{'title'},
      link        => $item->{'link'},
      description => $item->{'description'},
      pubDate     => $item->{'pubDate'},
      author      => $item->{'author'},
      guid        => $item->{'guid'},
      category    => $item->{'category'},
      media => {
        title     => $item->{'title'},
        text      => $item->{'description'},
        content => {
          url     => $item->{'enclosure'}->{'url'},
          type    => "image/jpeg",
          height  => "100",  # change later
          width   => "100"
        },
        thumbnail => {
          url     => $item->{'enclosure'}->{'url'},
          height  => "100",  # change later
          width   => "100"
        }
      }
   );
}

print "Content-Type: text/xml\n\n";
$s2frss->{output} = "2.0";
print $s2frss->as_string;
