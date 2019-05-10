#!/usr/local/bin/perl
# bemanager-lib.pl

BEGIN { push(@INC, ".."); };
use WebminCore;
use POSIX qw(strftime);
&init_config();

sub get_beadm_version
{
my $getversion = "$config{'beadm_path'} version";
my $version = `$getversion`;
}

# Gather boot environments information with beadm.
sub get_be_info
{
	my $beinfo = `$config{'beadm_path'} list -a -s`;
}
sub check_be_active
{
	my ($zfsbe) = @_;
	my $be_active = `$config{'beadm_path'} list -H | grep ${zfsbe} | grep -wE 'NR|R'`;
}
sub check_be_root
{
	my ($zfsbe) = @_;
	my $be_root = `$config{'beadm_path'} list -H | grep ${zfsbe} | grep -wE 'NR|N'`;
}

# Get boot environment montpoint.
sub check_be_mount
{
	my ($zfsbe) = @_;
	my $be_mountcheck = `df | grep ${zfsbe}`;
}

# Get the rootfs and bootfs.
sub get_zroot_dataset
{
	my $rootfs = `mount | awk '\/ \\/ \/ {print \$1}'`;
	chomp ($rootfs);
	my $pool = `echo '${rootfs}' | awk -F '\/' '{print \$1}'`;
	chomp ($pool);
	my $zroot_dataset = `zpool list -H -o bootfs '${pool}' | sed "s|/[^/]*\$||"`;
}

# List boot environments.
sub list_bootenvs
{
my ($bootenv) = @_;
$list=`$config{'beadm_path'} list -H`;
$idx = 0;
open my $fh, "<", \$list;
while (my $line =<$fh>)
{
	chomp ($line);
	my @props = split("\x09", $line);
	$ct = 0;
	foreach $prop (split(",", "name,active,mountpoint,space,created" )) {
		$bootenv{sprintf("%05d", $idx)}{$prop} = $props[$ct];
		$ct++;
	}
	$idx++;
}
return %bootenv;
}

# UI list boot environments.
sub ui_list_bootenvs
{
my ($bootenv, $admin) = @_;
%bootenv = list_bootenvs($bootenv);
@props = split(",", "active,mountpoint,space,created" );
print &ui_columns_start([ "$text{'colprop_name'}", "$text{'colprop_active'}", "$text{'colprop_mountdir'}", "$text{'colprop_space'}", "$text{'colprop_created'}" ]);
my $num = 0;
foreach $key (sort(keys %bootenv))
{
	@vals = ();
	foreach $prop (@props) { push (@vals, $bootenv{$key}{$prop}); }
	if ($config{'bootenv_tasks'} =~ /1/) {
		print &ui_columns_row([ "<a href='tasks.cgi?bootenv=$bootenv{$key}{'name'}'>$bootenv{$key}{'name'}</a>", @vals ]);
		$num ++;
	} else {
		print &ui_columns_row([ $bootenv{$key}{'name'}, @vals ]);
	}
}
print &ui_columns_end();
print &ui_form_end();
}

sub ui_create_bootenv
{
#my ($zfsbe) = @_;
$rv = &ui_form_start('cmd.cgi', 'post')."\n";
my $date = strftime "bename_%Y-%m-%d-%H%M%S", localtime;
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";
$rv .= &ui_hidden('cmd', "bootenv")."\n";
$rv .= &ui_submit("$text{'button_create'}");
$rv .= &ui_textbox('bootenv', $date, 20)."\n";
$rv .= "$text{'blabel_newbe'}<br />\n";
$rv .= &ui_form_end();
return $rv;
}

sub ui_activate_bootenv
{
my ($zfsbe) = @_;
if (check_be_active($zfsbe)) {
	$state_act = "disable";
	}

$rv = &ui_form_start('cmd.cgi', 'post')."\n";
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";
$rv .= &ui_hidden('cmd', "activatebe")."\n";
$rv .= &ui_submit("$text{'button_activate'}", state => "${state_act}");
$rv .= "$text{'blabel_activate'} <i>".$zfsbe."<br />\n";
$rv .= &ui_form_end();
return $rv;
}

sub ui_mount_bootenv
{
my ($zfsbe) = @_;
if (check_be_root($zfsbe)) {
	$state_mnt = "disable";
	}

$rv = &ui_form_start('cmd.cgi', 'post')."\n";
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";

if (check_be_mount($zfsbe)) {
	$rv .= &ui_hidden('cmd', "beunmount")."\n";
	$rv .= &ui_submit("$text{'button_unmount'}", state => "${state_mnt}");
	$rv .= "$text{'blabel_unmount'} <i>".$zfsbe."<br />\n";
} else {
	$rv .= &ui_hidden('cmd', "mountbe")."\n";
	$rv .= &ui_submit("$text{'button_mount'}", state => "${state_mnt}");
	$rv .= "$text{blabel_mount} <i>".$zfsbe."<br />\n";
}

$rv .= &ui_form_end();
return $rv;
}

sub ui_rename_bootenv
{
my ($zfsbe) = @_;
$rv = &ui_form_start('cmd.cgi', 'post')."\n";
my $date = strftime "bename_%Y-%m-%d-%H%M%S", localtime;
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";
$rv .= &ui_hidden('cmd', "renamebe")."\n";
$rv .= &ui_submit("$text{'button_rename'}");
$rv .= &ui_textbox('bootenv', $date, 20)."\n";
$rv .= "$text{'blabel_rename'} <i>".$zfsbe."<br />\n";
$rv .= &ui_form_end();
return $rv;
}

sub ui_backup_bootenv
{
my ($zfsbe) = @_;
$rv = &ui_form_start('cmd.cgi', 'post')."\n";
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";
$rv .= &ui_hidden('cmd', "backupbe")."\n";
$rv .= &ui_submit("$text{'button_backup'}");
$rv .= "$text{'blabel_backup'} <i>".$zfsbe."<br />\n";
$rv .= &ui_form_end();
return $rv;
}

sub ui_restore_bootenv
{
my ($zfsbe) = @_;
$rv = &ui_form_start('cmd.cgi', 'post')."\n";
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";
$rv .= &ui_hidden('cmd', "restorebe")."\n";
$rv .= &ui_submit("$text{'button_restore'}");
$rv .= &ui_filebox('befile')."\n";
$rv .= "$text{'blabel_restore'}<br />\n";
$rv .= &ui_form_end();
return $rv;
}

sub ui_destroy_bootenv
{
my ($zfsbe) = @_;
if (check_be_active($zfsbe) || check_be_root($zfsbe)) {
	$state_del = "disable";
	}

$rv = &ui_form_start('cmd.cgi', 'post')."\n";
$rv .= &ui_hidden('zfsbe', $zfsbe)."\n";
$rv .= &ui_hidden('cmd', "destroybe")."\n";
$rv .= &ui_submit("$text{'button_delete'}", state => "${state_del}");
$rv .= "$text{'blabel_delete'} <i>".$zfsbe."<br />\n";
$rv .= &ui_checkbox('force', '-f', "$text{'blabel_force'}");
$rv .= &ui_form_end();
return $rv;
}

sub ui_cmd
{
my ($message, $cmd) = @_;
print "$text{'cmd_'.$in{'cmd'}} $message $text{'index_withcmd'}<br />\n";
print "<i># ".$cmd."</i><br /><br />\n";
if (!$in{'confirm'}) {
	print &ui_form_start('cmd.cgi', 'post');
	foreach $key (keys %in) {
		print &ui_hidden($key, $in{$key});
	}
	print "<h3>$text{'index_continue'}</h3>\n";
	print &ui_submit("$text{'button_yes'}", "confirm", 0)."<br />";
	print &ui_form_end();
} else {
	@result = (`$cmd 2>&1`);
	if (!$result[0])
	{
		print "$text{'index_success'} <br />\n";
	} else	{
	print "<b>$text{'index_output'} </b>".$result[0]."<br />\n";
	foreach $key (@result[1..@result]) {
		print $key."<br />\n";
	}
	}
}
print "<br />";
}

1;
