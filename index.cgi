#!/usr/local/bin/perl
# index.cgi

require './bemanager-lib.pl';

# Check if beadm exists.
if (!&has_command($config{'beadm_path'})) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_errbeadm', "<tt>$config{'beadm_path'}</tt>",
		"$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
	}

# Check if BE mount dir is defined.
if (!($config{'be_mountpath'})) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_errmountpath', "<tt>$config{'be_mountpath'}</tt>",
		"$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
	}

# Check if BE backup dir is defined.
if (!($config{'be_backupdir'})) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_errbackupdir', "<tt>$config{'be_backupdir'}</tt>",
		"$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
	}

# Get beadm version.
my $version = &get_beadm_version();
if (!$version == "blank") {
	# Display version.
	&write_file("$module_config_directory/version", {""},$version);
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1, 0,
		&help_search_link("beadm", "man", "doc", "google"), undef, undef,
		&text('index_version', "$text{'index_modver'} $version"));
	}
else {
	# Don't display version.
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1, 0,
		&help_search_link("beadm", "man", "doc", "google"), undef, undef,
		&text('index_version', ""));
}

# Start tabs.
@tabs = ();

if ($config{'show_bootenv'} =~ /1/) {
	push(@tabs, [ "bootenv", "Boot Environments", "index.cgi?mode=bootenv" ]);
	}
if ($config{'show_beinfo'} =~ /1/) {
	push(@tabs, [ "info", "Information", "index.cgi?mode=info" ]);
	}

print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || $tabs[0]->[0], 1);

# Start boot environments tab.
if ($config{'show_bootenv'} =~ /1/) {
	print &ui_tabs_start_tab("mode", "bootenv");
	&ui_list_bootenvs(undef, 1);
	print &ui_tabs_end_tab("mode", "bootenv");
}

# Start boot environments info tab.
if ($config{'show_beinfo'} =~ /1/) {
	print &ui_tabs_start_tab("mode", "info");	
	local $out = get_be_info();
	print "<pre>$out</pre>";
	print &ui_tabs_end_tab("mode", "info");
}

# End tabs.
print &ui_tabs_end(1);
&ui_print_footer("/", $text{'index'});
