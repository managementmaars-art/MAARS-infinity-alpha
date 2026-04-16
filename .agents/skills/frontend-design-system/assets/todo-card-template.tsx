// Task Card Component Template
// Supports: shadcn/ui, Material UI, Chakra UI

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { MoreVertical, Trash2, Edit, Check } from "lucide-react"

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  priority?: 'high' | 'medium' | 'low'
  tags?: string[]
  dueDate?: Date
}

interface TaskCardProps {
  task: Task
  onToggleComplete?: (id: string) => void
  onEdit?: (id: string) => void
  onDelete?: (id: string) => void
}

export function TaskCard({ task, onToggleComplete, onEdit, onDelete }: TaskCardProps) {
  const priorityColors = {
    high: 'destructive',
    medium: 'default',
    low: 'secondary'
  } as const

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start gap-3">
          {/* Checkbox */}
          <Checkbox
            id={`task-${task.id}`}
            checked={task.completed}
            onCheckedChange={() => onToggleComplete?.(task.id)}
            className="mt-1"
          />

          {/* Content */}
          <div className="flex-1 min-w-0">
            <label
              htmlFor={`task-${task.id}`}
              className={`text-base font-medium cursor-pointer block ${
                task.completed ? 'line-through text-muted-foreground' : ''
              }`}
            >
              {task.title}
            </label>

            {task.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {task.description}
              </p>
            )}

            {/* Meta information */}
            <div className="flex flex-wrap gap-2 mt-3">
              {task.priority && (
                <Badge variant={priorityColors[task.priority]}>
                  {task.priority}
                </Badge>
              )}
              {task.tags?.map(tag => (
                <Badge key={tag} variant="outline">
                  {tag}
                </Badge>
              ))}
              {task.dueDate && (
                <Badge variant="outline" className="text-xs">
                  Due: {new Date(task.dueDate).toLocaleDateString()}
                </Badge>
              )}
            </div>
          </div>

          {/* Actions */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {!task.completed && (
                <DropdownMenuItem onClick={() => onToggleComplete?.(task.id)}>
                  <Check className="mr-2 h-4 w-4" />
                  Mark Complete
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={() => onEdit?.(task.id)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete?.(task.id)}
                className="text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardContent>
    </Card>
  )
}

// Alternative: Compact List Item Version
export function TaskListItem({ task, onToggleComplete, onEdit, onDelete }: TaskCardProps) {
  return (
    <div className="flex items-center gap-3 py-3 px-4 hover:bg-accent/50 rounded-lg transition-colors group">
      <Checkbox
        checked={task.completed}
        onCheckedChange={() => onToggleComplete?.(task.id)}
      />
      <div className="flex-1 min-w-0">
        <span className={task.completed ? 'line-through text-muted-foreground' : ''}>
          {task.title}
        </span>
      </div>
      {task.priority && (
        <Badge variant={task.priority === 'high' ? 'destructive' : 'secondary'} className="shrink-0">
          {task.priority}
        </Badge>
      )}
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="icon" onClick={() => onEdit?.(task.id)}>
          <Edit className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={() => onDelete?.(task.id)}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
