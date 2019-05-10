#!/usr/local/bin/perl
# cmd.cgi

require './bemanager-lib.pl';
use POSIX qw(strftime);
&ReadParse();

&ui_print_header(undef, $text{'index_cmdtitle'}, "", undef, 1, 1);

if ($config{'be_mountpath'}) {
		$be_mountpoint = "$config{'be_mountpath'}/$in{'zfsbe'}_BE";
		$be_rmdir = "&& rm -rf";
		}

print &ui_table_start($text{'index_cmdtitle'}, "width=100%", "10", ['align=left'] );

if ($in{'cmd'} =~ "bootenv")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "beadm create ".$in{'zfsbe'}."".$in{'bootenv'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'bootenv'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "activatebe")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "beadm activate ".$in{'zfsbe'}."".$in{'activatebe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'activatebe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "renamebe")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "beadm rename ".$in{'zfsbe'}." ".$in{'bootenv'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'renamebe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "mountbe")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "beadm mount ".$in{'zfsbe'}." ${be_mountpoint} ".$in{'mountbe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'mountbe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "beunmount")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "beadm unmount ".$in{'zfsbe'}." ${be_rmdir} ${be_mountpoint} ".$in{'beunmount'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'beunmount'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "destroybe")  {

	# Force delete confirm.
	if ($in{'force'}) {
		$forceopt = "-F";
		}
	else {
		$sayyes = "echo 'y' |";
		}

	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "${sayyes} beadm destroy ${forceopt} ".$in{'zfsbe'}."".$in{'destroybe'} : undef;
	$in{'confirm'} = "yes";
	#if ($in{'confirm'})
	#{
	#	print $text{'cmd_destroy'}." $in{'zfsbe'}... <br />";
	#	print "<br />";
	#	print &ui_form_start('cmd.cgi', 'post');
	#	print &ui_hidden('cmd', $in{'destroybe'});
	#	print &ui_hidden('zfsbe', $in{'zfsbe'});
	#	print "<h3>$text{'index_warning'}</h3>";
	#	print &ui_checkbox('confirm', 'yes', $text{'index_understand'}, undef );
	#	print &ui_hidden('checked', 'no');
	#	if ($in{'checked'} =~ /no/) { print " <font color='red'> -- $text{'index_checkbox'}</font>"; }
	#	print "<br /><br />";
	#	print &ui_submit($text{'button_continue'}, undef, undef);
	#	print &ui_form_end();
	#} else {
	#	$in{'confirm'} = "yes";
		&ui_cmd($in{'destroybe'}, $cmd);
	#}
	#^^^ Warning confirmation doesn't work for some reason.
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "backupbe")  {
	my $zroot_dataset = get_zroot_dataset();
	chomp($zroot_dataset);
	my $snap_date = strftime "%Y-%m-%d-%H%M%S", localtime;
	my $backup_date = strftime "$in{'zfsbe'}-${snap_date}", localtime;

	# Check for the backup directory.
	if ($config{'be_backupdir'}) {
		$bakupdir = $config{'be_backupdir'};
		unless(-e $bakupdir or mkdir $bakupdir) {
			die "Unable to create $bakupdir\n";
			}
		}
	else {
		die "Backup directory not defined\n";
		}

	# Always take a recent snapshot of the boot environment before backup.
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "zfs snapshot ${zroot_dataset}/$in{'zfsbe'}\@${snap_date} && zfs send $config{'zfs_sendparam'} ${zroot_dataset}/$in{'zfsbe'}\@${snap_date} | $config{'be_compress'} > ${bakupdir}/${backup_date}.zfs".$in{'backupbe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'backupbe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "restorebe")  {
	my $zroot_dataset = get_zroot_dataset();
	chomp($zroot_dataset);
	my $restore_date = strftime "restore-%Y-%m-%d-%H%M%S", localtime;
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "$config{'be_decompress'} $in{'befile'} | zfs receive $config{'zfs_recvparam'} ${zroot_dataset}/${restore_date}".$in{'backupbe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'backupbe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}

print &ui_table_end();
if (@footer) {
	&ui_print_footer(@footer);
	}
if ($in{'zfsbe'} && !@footer) {
	print "<br />";
	&ui_print_footer("tasks.cgi?zfsbe=".$in{'zfsbe'}, $in{'zfsbe'});
	}
