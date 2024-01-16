<#
TechNet Contribution: Measure-Command with Multiple Commands, Repetitions, Calculated Averages
Previous link: https://gallery.technet.microsoft.com/Measure-Command-with-52158178
Downloaded: 529 times (as of 05/21/2020)

In Windows PowerShell, there are often several ways to complete the same task. With that in mind, it makes sense that
we might want to determine how long commands and scripts take to complete. Until now, Measure-Command has been the
cmdlet we’ve used. While Measure-Command has been helpful, I’ve often thought it should include some additional
functionality. Therefore, I’ve written an advanced function, Measure-TMCommand, that adds all the benefits listed below:

– Continually measure the execution time of a single command and/or script, up to a user-defined number of repetitions.

– Continually measure the execution time of multiple commands and/or scripts, up to a user-defined number of repetitions.

– Calculate the average time a command(s), and/or a script(s), takes to execute.

– Display limited hardware information about the computer where the command and/or script is being measured.

– Includes an option to display the output of the command and/or script, as well as the measurement results.

– Updated 4/16/2015 (v1.2.1): Added a parameter -TimeInBetweenSeconds with a parameter alias of -Pause. This will pause
the function between executions, allowing the ability to test at different times between a set time. For instance, let's
say you want to measure a command every 1/2 hour for six hours: 12 repetitions with 30 minute pauses. You would then run
the command with the -Repetitions parameter with a value of 12 and the -TimeInBetweenSeconds (or -Pause) with a value of
1800 (as in 1800 seconds, or 30 minutes).

See the function in action at: http://tommymaynard.com/ss-an-improved-measure-command-multiple-commands-multiple-repetitions-and-calculated-averages-2015/
#>

Function Measure-TMCommand {
<#

.SYNOPSIS
    Continually measure a command (or commands) and/or a script (or scripts) up to a user-defined number of repetitions.

.DESCRIPTION
    Continually measure a command (or commands) and/or a script (or scripts) up to a user-defined number of repetitions. As well, the advanced function will calculate averages, can include limited hardware specs about the computer that is performing the measurements, and can even display the output of the commands and/or scripts being measured.

.PARAMETER Command
    The string, or strings, used as this parameter's value will have their execution time measured.

.PARAMETER Repetitions
    This parameter defines the number of times commands and/or scripts are measured.

.PARAMETER SystemInfo
    This parameter will provide limited hardware information about the computer where the measurements are taking place.

.PARAMETER ShowOutput
    This parameter will execute the commands and/or scripts, as well as measure them. Externally displaying the output will likely increase measurement times and averages.

.EXAMPLE
    Measure-TMCommand -Command 'Get-Service' -Repetitions 5

    This example measures the execution time of the Get-Service cmdlet for 5 repetitions. It will display the noticiation text.

.EXAMPLE
    Measure-TMCommand 'Get-Service','Get-Process' -Reps 10 | Format-Table * -Autosize

    This example measures the execution time of the Get-Service and Get-Process cmdlets for 10 repetitions each, and formats that information into a table that includes all the properties.

.EXAMPLE
    Measure-TMCommand 'Get-Eventlog Security' 3 -Sys | Select-Object Command,Repetition,Average*

    This example measures the execution time of a Get-EventLog command for 3 repetitions. It will display limited hardware information about the system where it is executed. It will only display the Command property, Repetition property, and any properties that begin with 'Average.'

.EXAMPLE
    Measure-TMCommand "Get-Service | where Name -like 'msi*'" 5 -ShowOutput | Export-Csv -Path C:\MeasureGetService.csv -NoTypeInformation

    This example measures the execution time two commands for 5 repetitions each. As well as formatting the information in a table, with all the properties and autosized, it will display the output of the Get-Service command it is measuring.

.EXAMPLE
    Measure-TMCommand 'c:\testscript.ps1' 5 -Verbose

    This example measures the execution time of the script located at c:\testscript.ps1 for 5 repetitions. It will display any Write-Verbose statements.

.NOTES
    Author: Tommy Maynard
    Email: tommy@tommymaynard.com
    Site: http://tommymaynard.com
    Last Update: 1.2.1: 2014-04-16

    Personal Note:
    - I have opted not to include the standard properties TotalDays, TotalHours, TotalMinutes, TotalSeconds, and TotalMilliseconds that are included with the Measure-Command cmdlet.

    Version 1.1:
    - Rewrote to use single PSCustomObject.
    - Modified Write-Output to Write-Host for $Notice, $SystemInfo, and for the -ShowOutput parameter.
    - Added warning for running with less than PowerShell 3.0.
    - Changed WMI Classes: CIM_ back to Win32_.
    Version 1.2:
    - Removed -HideNotice parmeter / Writing Notice text using -Verbose.
    - Moved Notice text into process block.
    - Modified Write-Host for $SystemInfo to Write-Verbose.
    Version 1.2.1:
    - Removed Notice text *completely*.
    - Removed use of ticks (time measurement smaller than milliseconds). These were commented out, so they can be added back easily.
    - Added Aliases for all the parameters except -Command.
#>

    [CmdletBinding()]
    Param (
        
        [Parameter(Mandatory=$true,Position=0)]
        [string[]]$Command,

        [Parameter(Position=1)]
        [Alias('Rep','Reps')]
        [int]$Repetitions = 1,

        [Alias('Pause')]
        [int]$TimeBetweenInSeconds,

        [Alias('Sys')]
        [switch]$SystemInfo,

        [Alias('Show')]
        [switch]$ShowOutput
    )

    Begin {
        Write-Verbose -Message 'Checking the version of PowerShell.'
        If ($PSVersionTable.PSVersion.Major -lt 3) {
            $WarningMessage = @"
-----------------------------------------------------------------
This advanced function has been developed for PowerShell 3.0 and greater. 
Using a lesser version may cause unexpected, or unintended, results.
Computer Name: $env:COMPUTERNAME.$env:USERDNSDOMAIN -- PowerShell Version: $($PSVersionTable.PSVersion.Major).0
--------------------------------------------------------------------------
"@
            Write-Warning -Message $WarningMessage
        } Else {
            Write-Verbose -Message 'PowerShell Version is at least version 3.0.'
        } # End If-Else.

        # Collect system information if -SystemInfo parameter is included
        If ($SystemInfo) {
            Write-Verbose -Message 'Getting system information.'
            $ComputerSystem = Get-CimInstance -ClassName Win32_ComputerSystem -Verbose:$false
            $ComputerOS = Get-CimInstance -ClassName Win32_OperatingSystem -Verbose:$false
            $ComputerCPU = Get-CimInstance -ClassName Win32_Processor -Verbose:$false

            Write-Verbose -Message '------ SYSTEM INFO -------------------------------------------------------' -Verbose
            Write-Verbose -Message "Operating System: $($ComputerOS.Caption) (Service Pack: $($ComputerOS.ServicePackMajorVersion))" -Verbose
            Write-Verbose -Message "Manufacturer: $($ComputerSystem.Manufacturer) ($($ComputerSystem.Model))" -Verbose
            Write-Verbose -Message "CPU: $($ComputerCPU.Name)" -Verbose
            Write-Verbose -Message ("RAM: $('{0:N2}' -f ($ComputerSystem.TotalPhysicalMemory/1GB))GB") -Verbose
            Write-Verbose -Message '--------------------------------------------------------------------------' -Verbose
        }
        Else {
            Write-Verbose -Message 'Skipping system information.'
        } # End If-Else.
    } #End Begin

    Process {
        $Object = @()
        Foreach ($C in $Command) {
            Write-Verbose -Message "Measuring $C."

            For ($i = 1; $i -le $Repetitions; $i++) {
                Write-Verbose -Message "Repetition $($i): Beginning of measurement."
            
                If (-not($ShowOutput)) {
                    $MeasuredCommand = Measure-Command -Expression ([scriptblock]::Create($C)) | 
                    Select-Object Hours,Minutes,Seconds,Milliseconds #,Ticks
                } Else {
                    $C2 = "$C | Out-Default"
                    Write-Verbose -Message "Command: $C (Repetition: $i)"
                    $MeasuredCommand = Measure-Command -Expression ([scriptblock]::Create($C2)) | 
                        Select-Object Hours,Minutes,Seconds,Milliseconds #,Ticks
                } #End If-Else.

                $TotalHours += $MeasuredCommand.Hours
                $TotalMinutes += $MeasuredCommand.Minutes
                $TotalSeconds += $MeasuredCommand.Seconds
                $TotalMilliseconds += $MeasuredCommand.Milliseconds 
                $TotalTicks += $MeasuredCommand.Ticks

                # Build object.
                $Object = [pscustomobject]@{
                    DateTime = Get-Date -Format G 
                    Command = $C;
                    Repetition = $i;
                    Hours = $MeasuredCommand.Hours;
                    Minutes = $MeasuredCommand.Minutes;
                    Seconds = $MeasuredCommand.Seconds;
                    Milliseconds = $MeasuredCommand.Milliseconds;
                    #Ticks = $MeasuredCommand.Ticks;
                    AverageHours = [math]::Round(($TotalHours / $i),3);
                    AverageMinutes = [math]::Round(($TotalMinutes / $i),3);
                    AverageSeconds = [math]::Round(($TotalSeconds / $i),3);
                    AverageMilliseconds = [math]::Round(($TotalMilliseconds / $i),3);
                    #AveragesTicks = [math]::Round(($TotalTicks / $i),3)
                } # End Object.

                #Write Object.
                Write-Verbose -Message "Repetition $($i): End of measurement."
                Write-Output -Verbose $Object

                If ($TimeBetweenInSeconds -and $i -ne $Repetitions) {
                    Write-Verbose -Message "Pausing for $TimeBetweenInSeconds seconds."
                    Start-Sleep -Seconds $TimeBetweenInSeconds
                } # End If.
            } # End For.

            Clear-Variable Total*
        } # End Foreach
    } # End Process
    End {
        Write-Verbose -Message "Completed (Object Count: $($Repetitions))"
    } # End, End
} # End Function