#!/usr/local/bin/perl
# tasks.cgi

require './bemanager-lib.pl';
&ReadParse();

# List boot environments.
if ($in{'bootenv'})
{
	&ui_print_header(undef, $text{'index_bootenv'}, "", undef, 1, 1);
	%bootenv = &list_bootenvs($in{'bootenv'});
	print &ui_columns_start([ "$text{'colprop_name'}", "$text{'colprop_active'}", "$text{'colprop_mountdir'}", "$text{'colprop_space'}", "$text{'colprop_created'}" ]);
	foreach $key (sort(keys %bootenv)) 
	{
		if ($bootenv{$key}{'mountpoint'} =~ "$config{'be_mountpath'}") {
			$bootenv{$key}{'mountpoint'} = "<a href='../filemin/index.cgi?path=$bootenv{$key}{'mountpoint'}'>$bootenv{$key}{'mountpoint'}</a>";
			}
		print &ui_columns_row(["<a href='tasks.cgi?bootenv=$bootenv{$key}{'name'}'>$bootenv{$key}{'name'}</a>", $bootenv{$key}{'active'}, $bootenv{$key}{'mountpoint'}, $bootenv{$key}{'space'}, $bootenv{$key}{'created'} ]);
	}
	print &ui_columns_end();

	my $zfsbe = $in{'bootenv'};
	$zfsbe =~ s/\@.*//;

	# Tasks table.
	#print &ui_table_start("$text{'index_tasks'} for : <i>".$zfsbe, 'width=100%', undef);
	print &ui_table_start("$text{'index_tasks'}", 'width=100%', undef);
	if ($config{'bootenv_tasks'} =~ /1/) {
		#print &ui_hr();
		print &ui_table_row(&ui_activate_bootenv($zfsbe));
		print &ui_table_row(&ui_rename_bootenv($zfsbe));
		print &ui_table_row(&ui_mount_bootenv($zfsbe));
		print &ui_table_row(&ui_create_bootenv($zfsbe));
		print &ui_table_row(&ui_backup_bootenv($zfsbe));
		print &ui_table_row(&ui_restore_bootenv($zfsbe));
		if ($config{'bootenv_destroy'} =~ /1/) {
			# Destroy task table.
			print &ui_table_start("$text{'index_destroy'}", 'width=100%', undef);
			print &ui_table_row(&ui_destroy_bootenv($zfsbe));
			print &ui_table_end();
			}
	}
	print &ui_table_end();
	print "<br><b>$text{'index_notes'}<b/><br>";
	print "$text{'index_notebackup'}<br/>";
	print "$text{'index_notetasks'}<br/>";
	print "$text{'index_noteprocess'}";
	&ui_print_footer('index.cgi?mode=bootenv', $text{'index_bootenv'});
}
