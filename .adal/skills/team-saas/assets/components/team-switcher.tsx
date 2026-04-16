"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTeams, useCreateTeam } from "@/hooks/use-teams";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { getInitials } from "@/lib/utils";

/**
 * Team Switcher Component
 * 
 * Dropdown to switch between teams and create new ones.
 * Typically placed in the sidebar header.
 */

interface TeamSwitcherProps {
  currentTeamId: string | null;
}

export function TeamSwitcher({ currentTeamId }: TeamSwitcherProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState("");

  const { data: teams = [], isLoading } = useTeams();
  const createTeam = useCreateTeam();

  const currentTeam = teams.find((t) => t.id === currentTeamId);

  const handleSelectTeam = (teamId: string) => {
    setOpen(false);
    router.push(`/teams/${teamId}`);
  };

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) return;

    const team = await createTeam.mutateAsync({ name: newTeamName.trim() });
    setCreateDialogOpen(false);
    setNewTeamName("");
    router.push(`/teams/${team.id}`);
  };

  return (
    <>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            aria-label="Select a team"
            className="w-full justify-between"
          >
            {currentTeam ? (
              <div className="flex items-center gap-2 truncate">
                <Avatar className="h-5 w-5">
                  <AvatarImage src={currentTeam.logo ?? undefined} />
                  <AvatarFallback className="text-[10px]">
                    {getInitials(currentTeam.name)}
                  </AvatarFallback>
                </Avatar>
                <span className="truncate">{currentTeam.name}</span>
              </div>
            ) : (
              <span className="text-muted-foreground">Select team...</span>
            )}
            <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[200px] p-0" align="start">
          <Command>
            <CommandInput placeholder="Search teams..." />
            <CommandList>
              <CommandEmpty>
                {isLoading ? "Loading..." : "No teams found."}
              </CommandEmpty>
              <CommandGroup heading="Teams">
                {teams.map((team) => (
                  <CommandItem
                    key={team.id}
                    value={team.name}
                    onSelect={() => handleSelectTeam(team.id)}
                    className="cursor-pointer"
                  >
                    <Avatar className="mr-2 h-5 w-5">
                      <AvatarImage src={team.logo ?? undefined} />
                      <AvatarFallback className="text-[10px]">
                        {getInitials(team.name)}
                      </AvatarFallback>
                    </Avatar>
                    <span className="truncate">{team.name}</span>
                    <Check
                      className={cn(
                        "ml-auto h-4 w-4",
                        currentTeamId === team.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
            <CommandSeparator />
            <CommandList>
              <CommandGroup>
                <CommandItem
                  onSelect={() => {
                    setOpen(false);
                    setCreateDialogOpen(true);
                  }}
                  className="cursor-pointer"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Team
                </CommandItem>
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Create Team Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Team</DialogTitle>
            <DialogDescription>
              Create a new team to collaborate with others.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="name">Team name</Label>
            <Input
              id="name"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Acme Inc."
              className="mt-2"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleCreateTeam();
                }
              }}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateTeam}
              disabled={!newTeamName.trim() || createTeam.isPending}
            >
              {createTeam.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
