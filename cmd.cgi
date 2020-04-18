#!/usr/local/bin/perl
# cmd.cgi

require './bemanager-lib.pl';
use POSIX qw(strftime);
&ReadParse();

&ui_print_header(undef, $text{'index_cmdtitle'}, "", undef, 1, 1);

print &ui_table_start($text{'index_cmdtitle'}, "width=100%", "10", ['align=left'] );

if ($in{'cmd'} =~ "bootenv")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "$config{'beadm_path'} create ".$in{'zfsbe'}."".$in{'bootenv'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'bootenv'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "activatebe")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "$config{'beadm_path'} activate ".$in{'zfsbe'}."".$in{'activatebe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'activatebe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "renamebe")  {
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "$config{'beadm_path'} rename ".$in{'zfsbe'}." ".$in{'bootenv'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'renamebe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "mountbe")  {
	my $be_mountpoint = "$config{'be_mountpath'}/$in{'zfsbe'}_BE";

	if ($config{'be_mountpath'}) {
	unless(-e $be_mountpoint or mkdir $be_mountpoint, 0700) {
			&backquote_command("mkdir -p -m 0700 $be_mountpoint");
		}
	} else {
		die "Mountpoint directory not defined\n";
	}

	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "$config{'beadm_path'} mount ".$in{'zfsbe'}." ${be_mountpoint} ".$in{'mountbe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'mountbe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "beunmount")  {
	my $be_mountpoint = "$config{'be_mountpath'}/$in{'zfsbe'}_BE";
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "$config{'beadm_path'} unmount ".$in{'zfsbe'}."".$in{'beunmount'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'beunmount'}, $cmd);
	&remove_mount_dir();
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "destroybe")  {

	# Force delete confirm.
	if ($in{'force'}) {
		$forceopt = "-F";
	} else {
		$sayyes = "echo 'y' |";
	}

	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "${sayyes} $config{'beadm_path'} destroy ${forceopt} ".$in{'zfsbe'}."".$in{'destroybe'} : undef;
	$in{'confirm'} = "yes";
	#if ($in{'confirm'}) {
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
	my $zroot_dataset = &get_zroot_dataset();
	chomp($zroot_dataset);
	my $snap_date = strftime "%Y-%m-%d-%H%M%S", localtime;
	my $backup_date = strftime "$in{'zfsbe'}-${snap_date}", localtime;

	# Check for the backup directory.
	&create_backup_dir();

	# Always take a recent snapshot of the boot environment before backup.
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "zfs snapshot ${zroot_dataset}/$in{'zfsbe'}\@${snap_date} && zfs send $config{'zfs_sendparam'} ${zroot_dataset}/$in{'zfsbe'}\@${snap_date} | xz $config{'be_compress'} > ${bakupdir}/${backup_date}.xz".$in{'backupbe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'backupbe'}, $cmd);
	@footer = ("index.cgi?mode=bootenv", $text{'index_bootenv'});
}
elsif ($in{'cmd'} =~ "restorebe")  {
	my $zroot_dataset = get_zroot_dataset();
	chomp($zroot_dataset);
	my $restore_date = strftime "restore-%Y-%m-%d-%H%M%S", localtime;
	my $cmd = ($config{'bootenv_tasks'} =~ /1/) ? "xz $config{'be_decompress'} $in{'befile'} | zfs receive $config{'zfs_recvparam'} ${zroot_dataset}/${restore_date}".$in{'backupbe'} : undef;
	$in{'confirm'} = "yes";
	&ui_cmd($in{'restorebe'}, $cmd);
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
