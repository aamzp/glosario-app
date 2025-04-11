import { Box, Text, HStack, IconButton, useColorModeValue } from "@chakra-ui/react"
import { ThumbsUp, ThumbsDown } from "lucide-react"
import { useState } from "react"

interface Props {
  id: string
  sentence: string
  page?: number
  score?: number
}

export function GlosarioCard({ sentence, page, score }: Props) {
  const [isLiked, setIsLiked] = useState<boolean | null>(null)

  const bgColor = useColorModeValue("gray.100", "gray.800")
  const textColor = useColorModeValue("gray.600", "gray.400")

  return (
    <Box
      w="full"
      p={4}
      borderRadius="xl"
      bg={bgColor}
      shadow="md"
      transition="all 0.2s"
    >
      <Text fontSize="lg" fontStyle="italic">“{sentence}”</Text>

      <Text fontSize="sm" mt={2} color={textColor}>
        {page !== undefined && <>📄 Página <strong>{page}</strong></>}
        {score !== undefined && <> · 🔍 Score: <strong>{score}</strong></>}
      </Text>

      <HStack spacing={4} mt={3}>
        <IconButton
          aria-label="Like"
          icon={<ThumbsUp />}
          colorScheme={isLiked === true ? "green" : "gray"}
          variant="ghost"
          onClick={() => setIsLiked(true)}
        />
        <IconButton
          aria-label="Dislike"
          icon={<ThumbsDown />}
          colorScheme={isLiked === false ? "red" : "gray"}
          variant="ghost"
          onClick={() => setIsLiked(false)}
        />
      </HStack>
    </Box>
  )
}
